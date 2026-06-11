from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
import re
import shutil
import tempfile

from .changes import load_metadata, resolve_change, save_metadata
from .specs import Requirement, parse_baseline_spec, parse_delta_spec
from .validation import validate_change


class ArchiveError(RuntimeError):
    pass


def _tasks_complete(tasks_path: Path) -> bool:
    text = tasks_path.read_text(encoding="utf-8")
    return re.search(r"(?m)^\s*-\s*\[\s\]", text) is None


def _render_baseline(domain: str, requirements: dict[str, Requirement]) -> str:
    lines = [
        f"# {domain.upper()} Requirement Specification",
        "",
        "## Purpose",
        "",
        f"Current approved behavior for the {domain} domain.",
        "",
        "## Requirements",
        "",
    ]
    for requirement in requirements.values():
        lines.extend(
            [
                f"### Requirement: {requirement.requirement_id} {requirement.title}",
                requirement.content.strip(),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    )
    temp_path = Path(handle.name)
    try:
        with handle:
            handle.write(content)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def archive_change(project: Path, change_id: str) -> Path:
    project = project.resolve()
    change_root = resolve_change(project, change_id)
    metadata = load_metadata(change_root)
    if metadata.get("status") != "verified":
        raise ArchiveError("Change must be verified before archive")

    tasks_path = change_root / "tasks.md"
    if not tasks_path.exists() or not _tasks_complete(tasks_path):
        raise ArchiveError("All implementation tasks must be complete before archive")

    report = validate_change(project, change_id, strict=True)
    if not report.valid:
        raise ArchiveError(report.format_text())

    baseline_requirements: dict[Path, dict[str, Requirement]] = {}
    baseline_domains: dict[Path, str] = {}
    for delta_path in change_root.glob("specs/**/*.md"):
        domain = delta_path.parent.name
        baseline_path = project / "specs" / domain / "spec.md"
        if baseline_path not in baseline_requirements:
            baseline_requirements[baseline_path] = (
                parse_baseline_spec(baseline_path.read_text(encoding="utf-8"))
                if baseline_path.exists()
                else {}
            )
            baseline_domains[baseline_path] = domain
        requirements = baseline_requirements[baseline_path]
        for delta in parse_delta_spec(delta_path.read_text(encoding="utf-8")):
            requirement_id = delta.requirement_id
            if delta.operation == "ADDED":
                if requirement_id in requirements:
                    raise ArchiveError(f"ADDED requirement already exists: {requirement_id}")
                requirements[requirement_id] = delta
            elif delta.operation == "MODIFIED":
                if requirement_id not in requirements:
                    raise ArchiveError(
                        f"MODIFIED requirement does not exist: {requirement_id}"
                    )
                requirements[requirement_id] = delta
            elif delta.operation == "REMOVED":
                if requirement_id not in requirements:
                    raise ArchiveError(
                        f"REMOVED requirement does not exist: {requirement_id}"
                    )
                del requirements[requirement_id]
    rendered_baselines = {
        path: _render_baseline(baseline_domains[path], requirements)
        for path, requirements in baseline_requirements.items()
    }

    archive_root = project / "changes" / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    destination = archive_root / f"{dt.date.today().strftime('%Y%m%d')}-{change_id}"
    if destination.exists():
        raise ArchiveError(f"Archive destination already exists: {destination}")

    for path, content in rendered_baselines.items():
        _atomic_write(path, content)

    metadata["status"] = "archived"
    metadata["archived_at"] = dt.date.today().isoformat()
    metadata["updated_at"] = dt.date.today().isoformat()
    save_metadata(change_root, metadata)
    shutil.move(str(change_root), str(destination))
    return destination
