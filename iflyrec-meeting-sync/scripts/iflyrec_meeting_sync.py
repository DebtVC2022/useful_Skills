from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


BASE_URL = "https://www.iflyrec.com"
DEFAULT_USER_AGENT = "iflyrecClient/26.05.2700"
DEFAULT_RETRY_STATE_PATH = Path(__file__).with_name("sync_retry_state.json")
RETRY_BACKOFF_MINUTES = (10, 20, 40, 60)


def appdata_dir() -> Path:
    return Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))


def default_config_path() -> Path:
    env_path = os.environ.get("IFLYREC_MEETING_SYNC_CONFIG")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent / "config.json"


def expand_path(value: str | os.PathLike[str]) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value))))


@dataclass(frozen=True)
class RuntimeConfig:
    target_dir: Path
    iflyrec_data_dir: Path
    iflyrec_log_dir: Path
    base_url: str = BASE_URL
    user_agent: str = DEFAULT_USER_AGENT
    since_days: int = 3
    update_obsidian_indexes: bool = True

    @classmethod
    def from_file(cls, config_path: Path) -> "RuntimeConfig":
        if not config_path.exists():
            raise RuntimeError(f"config not found: {config_path}")
        data = json.loads(config_path.read_text(encoding="utf-8"))
        target_raw = data.get("target_dir") or os.environ.get("IFLYREC_MEETING_TARGET_DIR")
        if not target_raw:
            raise RuntimeError("target_dir missing in config or IFLYREC_MEETING_TARGET_DIR")

        data_dir = expand_path(data.get("iflyrec_data_dir") or (appdata_dir() / "iflyrecAssistant"))
        log_dir = expand_path(data.get("iflyrec_log_dir") or (data_dir / "logs"))
        return cls(
            target_dir=expand_path(target_raw),
            iflyrec_data_dir=data_dir,
            iflyrec_log_dir=log_dir,
            base_url=str(data.get("base_url") or BASE_URL).rstrip("/"),
            user_agent=str(data.get("user_agent") or DEFAULT_USER_AGENT),
            since_days=int(data.get("since_days") or 3),
            update_obsidian_indexes=bool(data.get("update_obsidian_indexes", True)),
        )


def load_session_id(iflyrec_data_dir: Path) -> str:
    store = iflyrec_data_dir / "datastore.json"
    raw = store.read_text(encoding="utf-8").strip()
    try:
        cfg = json.loads(base64.b64decode(raw + "=="))
    except Exception:
        cfg = json.loads(raw)
    sid = cfg.get("sid")
    if not sid:
        raise RuntimeError(f"sid not found in {store}")
    return str(sid)


def api_headers(cfg: RuntimeConfig, sid: str) -> dict[str, str]:
    return {
        "X-Biz-Id": "tjzs",
        "X-Session-Id": sid,
        "User-Agent": cfg.user_agent,
        "Accept": "application/json, text/plain, */*",
        "Origin": cfg.base_url,
        "Referer": f"{cfg.base_url}/aboutPage/",
    }


def api_json(cfg: RuntimeConfig, sid: str, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = api_headers(cfg, sid)
    payload = None
    if body is not None:
        headers["Content-Type"] = "application/json;charset=UTF-8"
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(cfg.base_url + path, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body_text[:300]}") from exc


def parse_log_candidates(log_dir: Path, since_days: int, now: dt.datetime | None = None) -> dict[str, dict[str, Any]]:
    now = now or dt.datetime.now()
    cutoff = now - dt.timedelta(days=since_days)
    timestamp_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?\]")
    url_re = re.compile(r"https://www\.iflyrec\.com/(?:homePage|aboutPage)/?\?[^ \]\"]+")
    records: dict[str, dict[str, Any]] = {}

    if not log_dir.exists():
        return records

    for log_path in sorted(log_dir.glob("debug-log.*.log")):
        if log_path.stat().st_mtime < cutoff.timestamp():
            continue
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for line in lines:
            time_match = timestamp_re.search(line)
            seen_at = None
            if time_match:
                try:
                    seen_at = dt.datetime.fromisoformat(time_match.group(1))
                except ValueError:
                    seen_at = None
            if seen_at and seen_at < cutoff:
                continue

            for url_match in url_re.finditer(line):
                url = url_match.group(0).rstrip(",")
                query = parse_qs(urlparse(url).query)
                order_id = first(query.get("orderId"))
                if not order_id:
                    continue
                audio_id = first(query.get("originAudioId"))
                existing = records.get(order_id)
                if not existing:
                    records[order_id] = {"order_id": order_id, "audio_id": audio_id, "seen_at": seen_at}
                    continue
                if audio_id and not existing.get("audio_id"):
                    existing["audio_id"] = audio_id
                if seen_at and (not existing.get("seen_at") or seen_at < existing["seen_at"]):
                    existing["seen_at"] = seen_at
    return records


def first(values: list[str] | None) -> str | None:
    return values[0] if values else None


def empty_retry_state() -> dict[str, Any]:
    return {"version": 1, "failures": {}}


def load_retry_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_retry_state()
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty_retry_state()
    if not isinstance(state, dict):
        return empty_retry_state()
    failures = state.get("failures")
    if not isinstance(failures, dict):
        state["failures"] = {}
    state["version"] = 1
    return state


def save_retry_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def parse_state_datetime(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def retry_delay_minutes(fail_count: int) -> int:
    index = min(max(fail_count, 1), len(RETRY_BACKOFF_MINUTES)) - 1
    return RETRY_BACKOFF_MINUTES[index]


def get_active_retry_failure(
    state: dict[str, Any],
    order_id: str,
    now: dt.datetime | None = None,
) -> dict[str, Any] | None:
    failures = state.get("failures")
    if not isinstance(failures, dict):
        return None
    entry = failures.get(order_id)
    if not isinstance(entry, dict):
        return None
    retry_after = parse_state_datetime(entry.get("retry_after"))
    if retry_after and retry_after > (now or dt.datetime.now()):
        return entry
    return None


def record_retry_failure(
    state: dict[str, Any],
    order_id: str,
    message: str,
    now: dt.datetime | None = None,
) -> None:
    failures = state.setdefault("failures", {})
    if not isinstance(failures, dict):
        failures = {}
        state["failures"] = failures
    current = failures.get(order_id) if isinstance(failures.get(order_id), dict) else {}
    failed_at = now or dt.datetime.now()
    fail_count = int(current.get("fail_count") or 0) + 1
    retry_after = failed_at + dt.timedelta(minutes=retry_delay_minutes(fail_count))
    failures[order_id] = {
        "fail_count": fail_count,
        "last_failed_at": failed_at.isoformat(timespec="seconds"),
        "retry_after": retry_after.isoformat(timespec="seconds"),
        "last_error": message[:500],
    }


def clear_retry_failure(state: dict[str, Any], order_id: str) -> None:
    failures = state.get("failures")
    if isinstance(failures, dict):
        failures.pop(order_id, None)


def is_retryable_skip(message: str) -> bool:
    return message.startswith(("skip incomplete ", "skip no audio id ", "skip no ai summary "))


def assert_success(data: dict[str, Any], label: str) -> None:
    if data.get("code") != "000000":
        raise RuntimeError(f"{label} failed: {data.get('code')} {data.get('desc')}")


def fetch_detail(cfg: RuntimeConfig, sid: str, order_id: str) -> dict[str, Any]:
    data = api_json(cfg, sid, "GET", f"/XFTJWebAdaptService/v1/hyjy/detail/{order_id}?fileSource=hj")
    assert_success(data, "detail")
    return data.get("biz") or {}


def fetch_ai_summary(cfg: RuntimeConfig, sid: str, order_id: str, audio_id: str) -> str:
    adaptive_error: Exception | None = None
    body = {"hjId": order_id, "fileSource": "hj", "originAudioId": audio_id}
    try:
        data = api_json(cfg, sid, "POST", "/XFTJWebAdaptService/v1/hyjy/web/aiPower/queryAdaptiveAISummaryResult", body)
        assert_success(data, "adaptive summary")
        biz = data.get("biz") or {}
        adaptive = biz.get("adaptiveSummary") or {}
        result = adaptive.get("aiResult") or biz.get("aiResult") or ""
        if result:
            return str(result)
    except Exception as exc:
        adaptive_error = exc

    try:
        fallback = api_json(
            cfg,
            sid,
            "GET",
            f"/XFTJWebAdaptService/v1/hj/aiPower/queryLastHyjyTaskResult"
            f"?hjId={order_id}&fileSource=hj&originAudioId={audio_id}",
        )
        assert_success(fallback, "last summary")
        return str((fallback.get("biz") or {}).get("aiResult") or "")
    except Exception as exc:
        if adaptive_error:
            raise RuntimeError(f"{adaptive_error}; fallback failed: {exc}") from exc
        raise


def fetch_transcript(cfg: RuntimeConfig, sid: str, order_id: str, audio_id: str) -> list[dict[str, Any]]:
    data = api_json(
        cfg,
        sid,
        "GET",
        f"/XFTJWebAdaptService/v1/hyjy/{order_id}/transcriptResults/16"
        f"?fileSource=hj&originAudioId={audio_id}",
    )
    assert_success(data, "transcript")
    raw = (data.get("biz") or {}).get("transcriptResult") or ""
    if not raw:
        return []
    obj = json.loads(raw) if isinstance(raw, str) else raw
    return parse_transcript_object(obj)


def fetch_insights(cfg: RuntimeConfig, sid: str, order_id: str, audio_id: str) -> list[dict[str, str]]:
    data = api_json(
        cfg,
        sid,
        "GET",
        f"/XFTJWebAdaptService/v1/hyjy/{order_id}/transcriptResults/58"
        f"?fileSource=hj&originAudioId={audio_id}",
    )
    assert_success(data, "insights")
    raw = (data.get("biz") or {}).get("transcriptResult") or ""
    if not raw:
        return []
    obj = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(obj, list):
        return []
    result: list[dict[str, str]] = []
    for item in obj:
        if not isinstance(item, dict):
            continue
        payload = item
        if isinstance(item.get("result"), str):
            try:
                parsed = json.loads(item["result"])
                if isinstance(parsed, dict):
                    payload = parsed
            except json.JSONDecodeError:
                payload = item
        title = str(payload.get("title") or payload.get("name") or "风险洞察").strip()
        text = str(payload.get("text") or payload.get("content") or payload.get("summary") or "").strip()
        if text:
            result.append({"title": title, "text": text})
    return result


def parse_transcript_object(obj: Any) -> list[dict[str, Any]]:
    paragraphs: list[dict[str, Any]] = []
    if isinstance(obj, dict) and isinstance(obj.get("ps"), list):
        for paragraph in obj["ps"]:
            if not isinstance(paragraph, dict):
                continue
            words = paragraph.get("words") or []
            text = "".join(str(word.get("text") or "") for word in words if isinstance(word, dict)).strip()
            if not text:
                continue
            p_time = paragraph.get("pTime") or []
            paragraphs.append(
                {
                    "role": str(paragraph.get("role") or paragraph.get("lastPsRole") or ""),
                    "start_ms": p_time[0] if len(p_time) > 0 else None,
                    "end_ms": p_time[1] if len(p_time) > 1 else None,
                    "text": text,
                }
            )
        return paragraphs

    if isinstance(obj, list):
        for paragraph in obj:
            if isinstance(paragraph, str):
                text = paragraph.strip()
                if text:
                    paragraphs.append({"role": "", "start_ms": None, "end_ms": None, "text": text})
            elif isinstance(paragraph, dict):
                text = str(paragraph.get("text") or paragraph.get("onebest") or paragraph.get("content") or "").strip()
                if text:
                    paragraphs.append(
                        {
                            "role": str(paragraph.get("role") or ""),
                            "start_ms": paragraph.get("start_ms") or paragraph.get("bg"),
                            "end_ms": paragraph.get("end_ms") or paragraph.get("ed"),
                            "text": text,
                        }
                    )
    return paragraphs


def find_imported_path(target_dir: Path, order_id: str) -> Path | None:
    for path in target_dir.glob("*.md"):
        try:
            if order_id in path.read_text(encoding="utf-8", errors="replace"):
                return path
        except OSError:
            continue
    return None


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"_+", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" ._")
    return value[:120] or "未命名会议"


def chinese_date(value: dt.datetime | dt.date) -> str:
    return f"{value.year}年{value.month}月{value.day}日"


def chinese_datetime(value: dt.datetime) -> str:
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{value.year}年{value.month}月{value.day}日（{weekdays[value.weekday()]}）{value:%H:%M}"


def format_duration(ms: int | None) -> str:
    if not ms:
        return ""
    seconds = round(ms / 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def format_mmss(ms: int | None) -> str:
    if ms is None:
        return "--:--"
    seconds = max(0, round(ms / 1000))
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def demote_markdown_headings(markdown: str) -> str:
    return re.sub(r"^(#{1,6})\s+", r"#\1 ", markdown.strip(), flags=re.MULTILINE)


def detail_duration_ms(detail: dict[str, Any]) -> int | None:
    for item in detail.get("fileList") or []:
        if isinstance(item, dict) and item.get("fileType") == "origin":
            return item.get("fileDuration")
    return None


def build_note(
    *,
    detail: dict[str, Any],
    order_id: str,
    audio_id: str,
    seen_at: dt.datetime | None,
    ai_summary: str,
    transcript: list[dict[str, Any]],
    insights: list[dict[str, str]],
) -> tuple[str, str]:
    title = str(detail.get("hjName") or "未命名会议").strip()
    record_time = seen_at or dt.datetime.now()
    duration_ms = detail_duration_ms(detail)
    end_time = record_time + dt.timedelta(milliseconds=duration_ms or 0)
    note_title = f"智能纪要：{title} {chinese_date(record_time)}"
    file_name = sanitize_filename(note_title) + ".md"
    duration_text = format_duration(duration_ms)
    time_line = chinese_datetime(record_time)
    if duration_ms:
        time_line += f" - {end_time:%H:%M}"
    time_line += "（GMT+08，本机日志推定）"

    lines: list[str] = [
        "---",
        "doc_role: process",
        "doc_status: active",
        "doc_authority: supporting",
        "doc_confidentiality: internal",
        'source_system: "iflyrec"',
        f'iflyrec_order_id: "{order_id}"',
        f'iflyrec_audio_id: "{audio_id}"',
        "tags:",
        "  - doc/authority/supporting",
        "  - doc/confidentiality/internal",
        "  - doc/role/process",
        "  - doc/status/active",
        "  - source/iflyrec",
        "---",
        f"# {note_title}",
        "",
        "> 来源：讯飞听见会记",
        "> ",
        f"> 录音主题：{title}",
        "> ",
        f"> 录音时间：{time_line}",
    ]
    if duration_text:
        lines.extend(["> ", f"> 录音时长：{duration_text}"])
    lines.extend(
        [
            "> ",
            f"> 讯飞会记 ID：`{order_id}`；音频 ID：`{audio_id}`",
            "",
            "> 智能纪要由 AI 生成，可能不准确，请结合原始转写甄别后使用。",
            "",
            "# 智能纪要",
            "",
            demote_markdown_headings(ai_summary) if ai_summary else "未拉取到智能纪要。",
            "",
            "# 风险洞察",
            "",
        ]
    )
    if insights:
        for item in insights:
            lines.append(f"- **{item['title']}**：{item['text']}")
    else:
        lines.append("未拉取到风险洞察。")

    lines.extend(["", "# 文字记录", ""])
    if transcript:
        for paragraph in transcript:
            role = paragraph.get("role")
            role_text = f"说话人{role}" if role not in (None, "") else "说话人"
            lines.append(f"- [{format_mmss(paragraph.get('start_ms'))}] **{role_text}**：{paragraph['text']}")
    else:
        lines.append("未拉取到文字记录。")

    lines.extend(
        [
            "",
            "# 自动化元数据",
            "",
            f"- 拉取时间：{dt.datetime.now():%Y-%m-%d %H:%M:%S}",
            "- 拉取方式：本机讯飞听见会记已生成结果接口",
            "- 权益消耗：未重新转写，仅拉取已生成结果",
            "",
        ]
    )
    return file_name, "\n".join(lines)


def unique_note_path(target_dir: Path, file_name: str) -> Path:
    path = target_dir / file_name
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    i = 2
    while True:
        candidate = target_dir / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def vault_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def direct_markdown_count(target_dir: Path) -> int:
    ignored = {"资料索引.md", "专题综合.core.md"}
    return sum(1 for path in target_dir.glob("*.md") if path.name not in ignored and not path.name.endswith(".core.md"))


def update_folder_index(target_dir: Path, new_files: list[Path]) -> None:
    index_path = target_dir / "资料索引.md"
    now = dt.datetime.now().replace(microsecond=0).isoformat()
    count = direct_markdown_count(target_dir)
    root = target_dir.parent.parent if target_dir.parent.exists() else target_dir
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
    else:
        text = (
            "---\n"
            f'generated: "{now}"\n'
            f'source_folder: "{vault_relative(target_dir, root)}"\n'
            "doc_role: common\n"
            "doc_status: active\n"
            "doc_authority: preferred\n"
            "doc_confidentiality: internal\n"
            "doc_rule: wiki-doc-governance-v1\n"
            "tags:\n"
            "  - core-folder-index\n"
            "  - doc/role/common\n"
            "  - doc/status/active\n"
            "  - doc/authority/preferred\n"
            "  - doc/confidentiality/internal\n"
            "  - doc/rule/wiki-doc-governance-v1\n"
            "---\n"
            "<!-- CORE_FOLDER_INDEX_V1 -->\n"
            f"# 资料索引：{target_dir.name}\n\n"
            f"- Source folder: `{vault_relative(target_dir, root)}`\n"
            "- Direct core files: 0\n"
            "- Recursive core files: 0\n\n"
            "## Direct core files\n"
            "\n## Local relationship highlights\n"
        )

    text = re.sub(r'generated: ".*?"', f'generated: "{now}"', text, count=1)
    text = re.sub(r"- Direct core files: \d+", f"- Direct core files: {count}", text, count=1)
    text = re.sub(r"- Recursive core files: \d+", f"- Recursive core files: {count}", text, count=1)

    additions = []
    for path in new_files:
        rel = vault_relative(path.with_suffix(""), root)
        line = f"- [[{rel}|{path.name}]] - `business_material`"
        if path.name not in text and line not in text:
            additions.append(line)
    if additions:
        insertion = "\n".join(additions) + "\n"
        marker = "\n## Local relationship highlights"
        if marker in text:
            text = text.replace(marker, "\n" + insertion + marker, 1)
        else:
            text = text.rstrip() + "\n" + insertion
    index_path.write_text(text, encoding="utf-8")


def import_candidate(
    cfg: RuntimeConfig,
    sid: str,
    candidate: dict[str, Any],
    dry_run: bool,
    force_update: bool,
) -> tuple[str, Path | None]:
    target_dir = cfg.target_dir
    order_id = candidate["order_id"]
    existing_path = find_imported_path(target_dir, order_id)
    if existing_path and not force_update:
        return f"skip imported {order_id}", None

    detail = fetch_detail(cfg, sid, order_id)
    if detail.get("hjStatus") != "completed" or detail.get("transcriptStatus") != "completed":
        return f"skip incomplete {order_id}", None

    audio_id = candidate.get("audio_id") or detail.get("originAudioId")
    if not audio_id:
        return f"skip no audio id {order_id}", None

    ai_summary = fetch_ai_summary(cfg, sid, order_id, str(audio_id))
    if not ai_summary:
        return f"skip no ai summary {order_id}", None

    transcript = fetch_transcript(cfg, sid, order_id, str(audio_id))
    insights = fetch_insights(cfg, sid, order_id, str(audio_id))
    file_name, note = build_note(
        detail=detail,
        order_id=order_id,
        audio_id=str(audio_id),
        seen_at=candidate.get("seen_at"),
        ai_summary=ai_summary,
        transcript=transcript,
        insights=insights,
    )
    note_path = existing_path or unique_note_path(target_dir, file_name)
    if not dry_run:
        note_path.write_text(note, encoding="utf-8")
    action = "updated" if existing_path else "imported"
    return f"{action} {order_id} -> {note_path.name}", note_path


def select_candidates(cfg: RuntimeConfig, order_id: str | None, audio_id: str | None, since_days: int) -> dict[str, dict[str, Any]]:
    candidates = parse_log_candidates(cfg.iflyrec_log_dir, since_days=since_days)
    if not order_id:
        return candidates
    existing = candidates.get(order_id)
    if existing:
        if audio_id:
            existing["audio_id"] = audio_id
        return {order_id: existing}
    return {order_id: {"order_id": order_id, "audio_id": audio_id, "seen_at": None}}


def command_self_test(cfg: RuntimeConfig) -> int:
    checks = [
        ("target parent", cfg.target_dir.parent.exists()),
        ("iflyrec data dir", cfg.iflyrec_data_dir.exists()),
        ("iflyrec log dir", cfg.iflyrec_log_dir.exists()),
        ("datastore", (cfg.iflyrec_data_dir / "datastore.json").exists()),
    ]
    for label, ok in checks:
        print(f"{label}: {'ok' if ok else 'missing'}")
    return 0 if all(ok for _, ok in checks) else 1


def command_scan(cfg: RuntimeConfig, since_days: int) -> int:
    candidates = parse_log_candidates(cfg.iflyrec_log_dir, since_days=since_days)
    for item in sorted(candidates.values(), key=lambda record: record.get("seen_at") or dt.datetime.max):
        print(json.dumps(item, ensure_ascii=False, default=str))
    if not candidates:
        print("no iflyrec meeting candidates found")
    return 0


def command_sync(args: argparse.Namespace, cfg: RuntimeConfig) -> int:
    cfg.target_dir.mkdir(parents=True, exist_ok=True)
    sid = load_session_id(cfg.iflyrec_data_dir)
    retry_state_path = Path(args.retry_state)
    retry_state = load_retry_state(retry_state_path)
    retry_state_dirty = False
    candidates = select_candidates(cfg, args.order_id, args.audio_id, args.since_days or cfg.since_days)
    if not candidates:
        print("no iflyrec meeting candidates found")
        return 0

    imported: list[Path] = []
    for candidate in sorted(candidates.values(), key=lambda item: item.get("seen_at") or dt.datetime.max):
        order_id = candidate.get("order_id")
        if not order_id:
            continue
        if not args.force_update:
            existing_path = find_imported_path(cfg.target_dir, order_id)
            if existing_path:
                clear_retry_failure(retry_state, order_id)
                retry_state_dirty = True
                print(f"skip imported {order_id}")
                continue
            retry_entry = get_active_retry_failure(retry_state, order_id)
            if retry_entry:
                print(
                    f"skip retry backoff {order_id} until "
                    f"{retry_entry.get('retry_after')}: {retry_entry.get('last_error')}"
                )
                continue
        try:
            message, path = import_candidate(cfg, sid, candidate, args.dry_run, args.force_update)
        except Exception as exc:
            message = f"skip error {order_id}: {exc}"
            print(message)
            if not args.dry_run:
                record_retry_failure(retry_state, order_id, message)
                retry_state_dirty = True
            continue
        print(message)
        if path:
            clear_retry_failure(retry_state, order_id)
            retry_state_dirty = True
            imported.append(path)
        elif is_retryable_skip(message) and not args.dry_run:
            record_retry_failure(retry_state, order_id, message)
            retry_state_dirty = True

    if imported and not args.dry_run and cfg.update_obsidian_indexes and not args.no_indexes:
        update_folder_index(cfg.target_dir, imported)
        print(f"updated index for {len(imported)} file(s)")
    elif args.dry_run:
        print("dry-run: no files written")
    if retry_state_dirty and not args.dry_run:
        save_retry_state(retry_state_path, retry_state)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync generated Xunfei Iflyrec meeting minutes to local Markdown files.")
    parser.add_argument("command", nargs="?", choices=["sync", "scan", "self-test"], default="sync")
    parser.add_argument("--config", default=str(default_config_path()), help="Path to runtime config.json.")
    parser.add_argument("--order-id", help="Import one known Iflyrec order id.")
    parser.add_argument("--audio-id", help="Optional origin audio id for --order-id.")
    parser.add_argument("--since-days", type=int, help="How many days of Iflyrec client logs to scan.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and report without writing files.")
    parser.add_argument("--force-update", action="store_true", help="Overwrite an already imported note for the same order id.")
    parser.add_argument("--no-indexes", action="store_true", help="Do not update Obsidian-style folder indexes.")
    parser.add_argument("--retry-state", default=str(DEFAULT_RETRY_STATE_PATH), help="Path to retry backoff state JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = RuntimeConfig.from_file(Path(args.config))

    if args.command == "self-test":
        return command_self_test(cfg)
    if args.command == "scan":
        return command_scan(cfg, args.since_days or cfg.since_days)
    return command_sync(args, cfg)


if __name__ == "__main__":
    raise SystemExit(main())
