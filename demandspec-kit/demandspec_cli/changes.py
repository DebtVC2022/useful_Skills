from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path
from typing import Any

import yaml

from .config import load_config
from .identifiers import stable_slug
from .resource_access import resource_path


def load_metadata(change_root: Path) -> dict[str, Any]:
    metadata_path = change_root / "metadata.yaml"
    data = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid change metadata: {metadata_path}")
    return data


def save_metadata(change_root: Path, metadata: dict[str, Any]) -> None:
    (change_root / "metadata.yaml").write_text(
        yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def resolve_change(project: Path, change_id: str) -> Path:
    change_root = project.resolve() / "changes" / change_id
    if not change_root.is_dir():
        raise FileNotFoundError(f"Change not found: {change_root}")
    return change_root


def create_change(
    project: Path,
    title: str,
    domain: str,
    change_type: str = "general",
    profile: str | None = None,
    owner: str = "待确认",
    change_id: str | None = None,
) -> Path:
    from .cli import init_project, new_demand

    project = project.resolve()
    init_project(project)
    config = load_config(project)
    selected_profile = profile or (
        "full"
        if change_type in config.get("full_profile_types", [])
        else config.get("default_profile", "lite")
    )
    if selected_profile not in config.get("profiles", {}):
        raise ValueError(f"Unknown profile: {selected_profile}")

    resolved_id = change_id or stable_slug(title, "change")
    change_root = project / "changes" / resolved_id
    if change_root.exists():
        raise FileExistsError(f"Change already exists: {change_root}")

    (change_root / "specs" / domain).mkdir(parents=True)
    template_root = resource_path("templates", "change")
    template_names = ["proposal.md", "acceptance.md", "tasks.md", "approval.md"]
    if selected_profile == "full":
        template_names.append("design.md")
    for name in template_names:
        shutil.copy2(template_root / name, change_root / name)
    shutil.copy2(template_root / "spec.md", change_root / "specs" / domain / "spec.md")

    demand_id = None
    if selected_profile == "full":
        demand_id = new_demand(project, title, change_type, owner).name

    today = dt.date.today().isoformat()
    metadata: dict[str, Any] = {
        "id": resolved_id,
        "title": title,
        "domain": domain,
        "type": change_type,
        "profile": selected_profile,
        "owner": owner,
        "reviewers": [],
        "status": "draft",
        "created_at": today,
        "updated_at": today,
    }
    if demand_id:
        metadata["demand_id"] = demand_id
    save_metadata(change_root, metadata)
    return change_root


def list_changes(project: Path) -> list[dict[str, Any]]:
    changes_root = project.resolve() / "changes"
    if not changes_root.exists():
        return []
    result = []
    for item in sorted(changes_root.iterdir()):
        if item.is_dir() and item.name != "archive" and (item / "metadata.yaml").exists():
            result.append(load_metadata(item))
    return result


def set_change_status(project: Path, change_id: str, new_status: str) -> Path:
    change_root = resolve_change(project, change_id)
    metadata = load_metadata(change_root)
    if new_status == "approved":
        raise ValueError("Use change approve to enter the approved state")
    if new_status == "archived":
        raise ValueError("Use change archive to enter the archived state")
    config = load_config(project)
    transitions = config.get("lifecycle", {}).get("transitions", {})
    current = metadata.get("status", "draft")
    allowed = transitions.get(current, [])
    if new_status not in allowed:
        raise ValueError(f"Invalid status transition: {current} -> {new_status}")
    metadata["status"] = new_status
    metadata["updated_at"] = dt.date.today().isoformat()
    save_metadata(change_root, metadata)
    return change_root


def approve_change(
    project: Path,
    change_id: str,
    approver: str,
    decision: str = "approved",
) -> Path:
    if decision != "approved":
        raise ValueError("Only approved decisions advance the lifecycle")
    change_root = resolve_change(project, change_id)
    metadata = load_metadata(change_root)
    if metadata.get("status") != "review":
        raise ValueError("Change must be in review before approval")
    (change_root / "approval.md").write_text(
        "\n".join(
            [
                "# Change Approval",
                "",
                f"- Decision: {decision}",
                f"- Approver: {approver}",
                f"- Date: {dt.date.today().isoformat()}",
                "- Conditions: none",
                "",
            ]
        ),
        encoding="utf-8",
    )
    metadata["status"] = "approved"
    metadata["approved_by"] = approver
    metadata["approved_at"] = dt.date.today().isoformat()
    metadata["updated_at"] = dt.date.today().isoformat()
    save_metadata(change_root, metadata)
    return change_root
