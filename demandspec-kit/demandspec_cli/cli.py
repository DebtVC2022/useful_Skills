from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import shutil
import sys
import textwrap

import yaml

from .archive import archive_change
from .changes import (
    approve_change,
    create_change,
    list_changes,
    load_metadata,
    resolve_change,
    set_change_status,
)
from .identifiers import stable_slug
from .resource_access import resource_root
from .validation import validate_change

try:
    from . import __version__
except Exception:
    __version__ = "0.1.0"

KIT_ROOT = resource_root()
REQUIRED_STAGES = [
    "00_intake",
    "01_clarify",
    "02_diagnose",
    "03_model",
    "04_prototype",
    "05_spec",
    "06_validate",
    "07_handoff",
    "08_archive",
]

TEMPLATE_MAP = {
    "00_intake/demand-card.md": "demand-card.md",
    "01_clarify/clarify-questions.md": "clarify-questions.md",
    "01_clarify/scope-boundary.md": "scope-boundary.md",
    "02_diagnose/ai-fit-assessment.md": "ai-fit-assessment.md",
    "03_model/business-process.md": "process-model.md",
    "03_model/data-fields.md": "data-fields.md",
    "03_model/business-rules.md": "business-rules.md",
    "04_prototype/prototype-spec.md": "prototype-spec.md",
    "04_prototype/figma-mastergo-spec.md": "figma-mastergo-spec.md",
    "05_spec/prd.md": "prd.md",
    "06_validate/acceptance-criteria.md": "acceptance-criteria.md",
    "06_validate/test-cases.md": "test-cases.md",
    "06_validate/review-checklist.md": "review-checklist.md",
    "07_handoff/dev-handoff.md": "dev-handoff.md",
    "08_archive/archive.md": "archive.md",
}

COMMANDS = [
    "demandspec-init",
    "demandspec-intake",
    "demandspec-clarify",
    "demandspec-scope",
    "demandspec-diagnose",
    "demandspec-ai-fit",
    "demandspec-model",
    "demandspec-data-rules",
    "demandspec-prototype",
    "demandspec-figma",
    "demandspec-prd",
    "demandspec-acceptance",
    "demandspec-review",
    "demandspec-handoff",
    "demandspec-archive",
    "demandspec-full",
    "demandspec-ai-scenario",
    "demandspec-meeting-to-prd",
    "demandspec-requirement-to-figma",
    "demandspec-prd-to-dev-tasks",
]


def slugify(text: str) -> str:
    return stable_slug(text, "demand")


def copy_if_missing(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return False
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)
    return True


def init_project(project: Path) -> None:
    project = project.resolve()
    (project / ".demandspec").mkdir(parents=True, exist_ok=True)
    (project / "demands").mkdir(parents=True, exist_ok=True)
    (project / "specs").mkdir(parents=True, exist_ok=True)
    (project / "changes" / "archive").mkdir(parents=True, exist_ok=True)

    copy_if_missing(KIT_ROOT / "configs" / "config.yaml", project / ".demandspec" / "config.yaml")
    copy_if_missing(KIT_ROOT / "configs" / "glossary.md", project / ".demandspec" / "glossary.md")
    copy_if_missing(KIT_ROOT / "configs" / "stakeholders.md", project / ".demandspec" / "stakeholders.md")
    copy_if_missing(KIT_ROOT / "configs" / "standards.md", project / ".demandspec" / "standards.md")

    tmpl_dst = project / ".demandspec" / "templates"
    tmpl_dst.mkdir(parents=True, exist_ok=True)
    for item in (KIT_ROOT / "templates").glob("*.md"):
        copy_if_missing(item, tmpl_dst / item.name)

    print(f"Initialized DemandSpec project at: {project}")


def new_demand(project: Path, name: str, demand_type: str = "general", owner: str = "待确认") -> Path:
    init_project(project)
    date = _dt.date.today().strftime("%Y%m%d")
    slug = slugify(name)
    demand_id = f"{date}-{slug}"
    demand_root = project.resolve() / "demands" / demand_id
    if demand_root.exists():
        raise FileExistsError(f"Demand already exists: {demand_root}")

    for stage in REQUIRED_STAGES:
        (demand_root / stage).mkdir(parents=True, exist_ok=True)

    template_root = KIT_ROOT / "templates"
    for rel, tmpl in TEMPLATE_MAP.items():
        copy_if_missing(template_root / tmpl, demand_root / rel)

    meta = demand_root / "00_intake" / "metadata.md"
    if not meta.exists():
        meta.write_text(textwrap.dedent(f"""
        # 需求元信息

        - 需求名称：{name}
        - 需求 ID：{demand_id}
        - 需求类型：{demand_type}
        - 负责人：{owner}
        - 创建日期：{_dt.date.today().isoformat()}
        - 当前阶段：00_intake
        - 当前状态：草稿
        """).strip() + "\n", encoding="utf-8")

    print(f"Created demand package: {demand_root}")
    return demand_root


def install_codex(project: Path) -> None:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    prompts = codex_home / "prompts"
    prompts.mkdir(parents=True, exist_ok=True)
    for item in (KIT_ROOT / "commands" / "codex").glob("*.md"):
        shutil.copy2(item, prompts / item.name)
    skill_dst = codex_home / "skills" / "demandspec"
    shutil.copytree(
        KIT_ROOT / "skills" / "demandspec",
        skill_dst,
        dirs_exist_ok=True,
    )
    copy_if_missing(KIT_ROOT / "rules" / "AGENTS.md", project / "AGENTS.md")
    print(f"Installed Codex prompts to: {prompts}")
    print(f"Installed Codex skill to: {skill_dst}")


def install_trae(project: Path) -> None:
    skill_dst = project / ".trae" / "skills" / "demandspec"
    skill_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT_ROOT / "skills" / "demandspec" / "SKILL.md", skill_dst / "SKILL.md")
    tmpl_dst = skill_dst / "templates"
    tmpl_dst.mkdir(parents=True, exist_ok=True)
    for item in (KIT_ROOT / "templates").glob("*.md"):
        shutil.copy2(item, tmpl_dst / item.name)
    rules_dst = project / ".trae" / "rules"
    rules_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT_ROOT / "rules" / "trae-demandspec-rules.md", rules_dst / "demandspec-rules.md")
    print(f"Installed Trae skill to: {skill_dst}")


def install_claude(project: Path) -> None:
    cmd_dst = project / ".claude" / "commands"
    cmd_dst.mkdir(parents=True, exist_ok=True)
    for item in (KIT_ROOT / "commands" / "claude").glob("*.md"):
        shutil.copy2(item, cmd_dst / item.name)
    copy_if_missing(KIT_ROOT / "rules" / "AGENTS.md", project / "AGENTS.md")
    print(f"Installed Claude commands to: {cmd_dst}")


def install_cursor(project: Path) -> None:
    rules_dst = project / ".cursor" / "rules"
    rules_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT_ROOT / "rules" / "cursor-demandspec.mdc", rules_dst / "demandspec.mdc")
    print(f"Installed Cursor rules to: {rules_dst}")


def install_target(project: Path, target: str) -> None:
    init_project(project)
    target = target.lower()
    if target in ("codex", "all"):
        install_codex(project)
    if target in ("trae", "all"):
        install_trae(project)
    if target in ("claude", "claude-code", "all"):
        install_claude(project)
    if target in ("cursor", "all"):
        install_cursor(project)
    if target not in ("codex", "trae", "claude", "claude-code", "cursor", "all"):
        raise SystemExit(f"Unknown target: {target}")


def status(project: Path) -> None:
    project = project.resolve()
    print(f"DemandSpec project: {project}")
    print(f".demandspec: {'OK' if (project/'.demandspec').exists() else 'MISSING'}")
    print(f"demands: {'OK' if (project/'demands').exists() else 'MISSING'}")
    demands_root = project / "demands"
    if not demands_root.exists():
        return
    demands = [p for p in demands_root.iterdir() if p.is_dir()]
    print(f"Demand packages: {len(demands)}")
    for d in demands:
        missing = [s for s in REQUIRED_STAGES if not (d / s).exists()]
        print(f"- {d.name}: {'OK' if not missing else 'MISSING ' + ', '.join(missing)}")


def validate(project: Path, demand_id: str | None = None) -> int:
    project = project.resolve()
    demands_root = project / "demands"
    if demand_id:
        candidates = [demands_root / demand_id]
    else:
        candidates = [p for p in demands_root.iterdir() if p.is_dir()] if demands_root.exists() else []

    issues = 0
    for d in candidates:
        if not d.exists():
            print(f"MISSING demand: {d}")
            issues += 1
            continue
        print(f"Validating {d.name}")
        for stage in REQUIRED_STAGES:
            if not (d / stage).exists():
                print(f"  MISSING stage: {stage}")
                issues += 1
        # lightweight quality checks
        prd = d / "05_spec" / "prd.md"
        acc = d / "06_validate" / "acceptance-criteria.md"
        if prd.exists() and not acc.exists():
            print("  MISSING acceptance-criteria.md for PRD")
            issues += 1
        if (d / "02_diagnose" / "ai-fit-assessment.md").exists():
            algo = d / "07_handoff" / "algorithm-tasks.md"
            if not algo.exists():
                print("  NOTICE: AI fit exists but algorithm-tasks.md is missing")
    if issues == 0:
        print("Validation passed.")
    else:
        print(f"Validation finished with {issues} issue(s).")
    return issues


def archive(project: Path, demand_id: str) -> None:
    project = project.resolve()
    demand = project / "demands" / demand_id
    if not demand.exists():
        raise SystemExit(f"Demand not found: {demand}")
    archive_dir = demand / "08_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    retrospective = archive_dir / "retrospective.md"
    if not retrospective.exists():
        shutil.copy2(KIT_ROOT / "templates" / "archive.md", retrospective)
    print(f"Archive assets prepared at: {archive_dir}")


def list_commands() -> None:
    print("Available DemandSpec commands:")
    for c in COMMANDS:
        print(f"/{c}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="demandspec", description="DemandSpec requirement-side AI harness CLI")
    parser.add_argument("--version", action="store_true", help="show version")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="initialize DemandSpec project")
    p_init.add_argument("--project", default=".")

    p_new = sub.add_parser("new", help="create a new demand package")
    p_new.add_argument("name")
    p_new.add_argument("--project", default=".")
    p_new.add_argument("--type", default="general")
    p_new.add_argument("--owner", default="待确认")

    p_install = sub.add_parser("install", help="install prompts/rules for a target tool")
    p_install.add_argument("target", choices=["codex", "trae", "claude", "cursor", "all"])
    p_install.add_argument("--project", default=".")

    p_status = sub.add_parser("status", help="show DemandSpec project status")
    p_status.add_argument("--project", default=".")

    p_validate = sub.add_parser("validate", help="validate DemandSpec structure")
    p_validate.add_argument("--project", default=".")
    p_validate.add_argument("--demand-id", default=None)
    p_validate.add_argument("--change-id", default=None)
    p_validate.add_argument("--strict", action="store_true")
    p_validate.add_argument("--json", action="store_true")

    p_archive = sub.add_parser("archive", help="prepare archive assets for demand")
    p_archive.add_argument("demand_id")
    p_archive.add_argument("--project", default=".")

    sub.add_parser("list-commands", help="list slash commands")

    p_change = sub.add_parser("change", help="manage requirement changes")
    change_sub = p_change.add_subparsers(dest="change_command")

    p_change_new = change_sub.add_parser("new", help="create a change")
    p_change_new.add_argument("title")
    p_change_new.add_argument("--domain", required=True)
    p_change_new.add_argument("--project", default=".")
    p_change_new.add_argument("--type", default="general")
    p_change_new.add_argument("--profile", choices=["lite", "full"], default=None)
    p_change_new.add_argument("--owner", default="待确认")
    p_change_new.add_argument("--id", default=None)

    p_change_list = change_sub.add_parser("list", help="list active changes")
    p_change_list.add_argument("--project", default=".")
    p_change_list.add_argument("--json", action="store_true")

    p_change_show = change_sub.add_parser("show", help="show change metadata")
    p_change_show.add_argument("change_id")
    p_change_show.add_argument("--project", default=".")
    p_change_show.add_argument("--json", action="store_true")

    p_change_status = change_sub.add_parser(
        "set-status",
        help="advance change lifecycle status",
    )
    p_change_status.add_argument("change_id")
    p_change_status.add_argument(
        "status",
        choices=[
            "clarifying",
            "review",
            "implementing",
            "verified",
        ],
    )
    p_change_status.add_argument("--project", default=".")

    p_change_approve = change_sub.add_parser("approve", help="approve a change")
    p_change_approve.add_argument("change_id")
    p_change_approve.add_argument("--approver", required=True)
    p_change_approve.add_argument("--project", default=".")

    p_change_validate = change_sub.add_parser("validate", help="validate a change")
    p_change_validate.add_argument("change_id")
    p_change_validate.add_argument("--project", default=".")
    p_change_validate.add_argument("--strict", action="store_true")
    p_change_validate.add_argument("--json", action="store_true")

    p_change_archive = change_sub.add_parser("archive", help="archive a change")
    p_change_archive.add_argument("change_id")
    p_change_archive.add_argument("--project", default=".")

    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0

    try:
        if args.command == "init":
            init_project(Path(args.project))
        elif args.command == "new":
            new_demand(Path(args.project), args.name, args.type, args.owner)
        elif args.command == "install":
            install_target(Path(args.project).resolve(), args.target)
        elif args.command == "status":
            status(Path(args.project))
        elif args.command == "validate":
            if args.change_id:
                report = validate_change(
                    Path(args.project),
                    args.change_id,
                    strict=args.strict,
                )
                print(
                    json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
                    if args.json
                    else report.format_text()
                )
                return 0 if report.valid else 1
            return validate(Path(args.project), args.demand_id)
        elif args.command == "archive":
            project = Path(args.project)
            if (project.resolve() / "changes" / args.demand_id).is_dir():
                destination = archive_change(project, args.demand_id)
                print(f"Archived change to: {destination}")
            else:
                archive(project, args.demand_id)
        elif args.command == "list-commands":
            list_commands()
        elif args.command == "change":
            if not args.change_command:
                p_change.print_help()
                return 1
            project = Path(args.project)
            if args.change_command == "new":
                change_root = create_change(
                    project,
                    args.title,
                    args.domain,
                    args.type,
                    args.profile,
                    args.owner,
                    args.id,
                )
                print(f"Created change: {change_root}")
            elif args.change_command == "list":
                changes = list_changes(project)
                if args.json:
                    print(json.dumps(changes, ensure_ascii=False, indent=2))
                else:
                    for item in changes:
                        print(
                            f"{item['id']}: {item['title']} "
                            f"[{item['profile']}/{item['status']}]"
                        )
            elif args.change_command == "show":
                metadata = load_metadata(resolve_change(project, args.change_id))
                print(
                    json.dumps(metadata, ensure_ascii=False, indent=2)
                    if args.json
                    else yaml.safe_dump(
                        metadata,
                        allow_unicode=True,
                        sort_keys=False,
                    ).rstrip()
                )
            elif args.change_command == "set-status":
                set_change_status(project, args.change_id, args.status)
                print(f"Change status updated: {args.change_id} -> {args.status}")
            elif args.change_command == "approve":
                approve_change(project, args.change_id, args.approver)
                print(f"Change approved: {args.change_id}")
            elif args.change_command == "validate":
                report = validate_change(
                    project,
                    args.change_id,
                    strict=args.strict,
                )
                print(
                    json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
                    if args.json
                    else report.format_text()
                )
                return 0 if report.valid else 1
            elif args.change_command == "archive":
                destination = archive_change(project, args.change_id)
                print(f"Archived change to: {destination}")
            else:
                p_change.print_help()
                return 1
        else:
            parser.print_help()
            return 1
    except (FileExistsError, FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
