from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from .changes import load_metadata, resolve_change
from .config import load_config
from .specs import (
    DELTA_HEADING,
    has_given_when_then,
    parse_baseline_spec,
    parse_delta_spec,
    requirement_ids,
)


REQUIRED_DEMAND_STAGES = (
    "00_intake",
    "01_clarify",
    "02_diagnose",
    "03_model",
    "04_prototype",
    "05_spec",
    "06_validate",
    "07_handoff",
    "08_archive",
)

PLACEHOLDER_MARKERS = (
    "DOMAIN-001",
    "Requirement name",
    "valid precondition",
    "observable behavior",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str = ""
    severity: str = "error"


@dataclass
class ValidationReport:
    change_id: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def add(
        self,
        code: str,
        message: str,
        path: Path | str = "",
        severity: str = "error",
    ) -> None:
        self.issues.append(
            ValidationIssue(code, message, str(path), severity)
        )

    def format_text(self) -> str:
        if not self.issues:
            return f"Change '{self.change_id}' is valid."
        lines = [f"Validation issues for '{self.change_id}':"]
        for issue in self.issues:
            location = f" [{issue.path}]" if issue.path else ""
            lines.append(
                f"- {issue.severity.upper()} {issue.code}{location}: {issue.message}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "change_id": self.change_id,
            "valid": self.valid,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "path": issue.path,
                    "severity": issue.severity,
                }
                for issue in self.issues
            ],
        }


def _section_body(text: str, heading: str) -> str | None:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else None


def _validate_proposal(change_root: Path, report: ValidationReport) -> None:
    proposal = change_root / "proposal.md"
    if not proposal.exists():
        return
    text = proposal.read_text(encoding="utf-8")
    for heading in ("Problem", "Intent", "Scope", "Non-Goals", "Impact", "Dependencies"):
        body = _section_body(text, heading)
        if not body:
            report.add(
                "placeholder-content",
                f"Proposal section '{heading}' is empty.",
                proposal,
            )


def _validate_design(
    change_root: Path,
    metadata: dict[str, object],
    report: ValidationReport,
) -> None:
    if metadata.get("profile") != "full":
        return
    design = change_root / "design.md"
    if not design.exists():
        return
    text = design.read_text(encoding="utf-8")
    for heading in ("Approach", "Components", "Data Flow", "Risks and Rollback", "Delivery Plan"):
        body = _section_body(text, heading)
        if not body:
            report.add(
                "empty-design-section",
                f"Design section '{heading}' is empty.",
                design,
            )


def _validate_placeholders(
    change_root: Path,
    report: ValidationReport,
    strict: bool,
) -> None:
    if not strict:
        return
    paths = [
        change_root / "proposal.md",
        change_root / "acceptance.md",
        change_root / "tasks.md",
        change_root / "design.md",
        *change_root.glob("specs/**/*.md"),
    ]
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        marker = next((item for item in PLACEHOLDER_MARKERS if item in text), None)
        if marker:
            report.add(
                "placeholder-content",
                f"Template placeholder remains: {marker}",
                path,
            )
        if "待确认" in text or "当前假设" in text:
            report.add(
                "unresolved-content",
                "Strict validation does not allow unresolved assumptions.",
                path,
            )


def _required_files(
    project: Path,
    change_root: Path,
    metadata: dict[str, object],
    report: ValidationReport,
) -> None:
    config = load_config(project)
    profile = str(metadata.get("profile", "lite"))
    profile_config = config.get("profiles", {}).get(profile)
    if not isinstance(profile_config, dict):
        report.add("unknown-profile", f"Unknown profile: {profile}")
        return
    for artifact in profile_config.get("required_artifacts", []):
        if "*" in artifact:
            if not list(change_root.glob(artifact)):
                report.add(
                    "missing-artifact",
                    f"Required artifact pattern has no matches: {artifact}",
                    change_root,
                )
        elif not (change_root / artifact).is_file():
            report.add(
                "missing-artifact",
                f"Required artifact is missing: {artifact}",
                change_root / artifact,
            )

    if profile_config.get("require_demand_package"):
        demand_id = metadata.get("demand_id")
        demand_root = project / "demands" / str(demand_id or "")
        if not demand_id or not demand_root.is_dir():
            report.add(
                "missing-demand-package",
                "Full profile requires a linked demand package.",
                demand_root,
            )
        else:
            missing = [
                stage for stage in REQUIRED_DEMAND_STAGES if not (demand_root / stage).is_dir()
            ]
            if missing:
                report.add(
                    "missing-demand-stage",
                    f"Linked demand package is missing stages: {', '.join(missing)}",
                    demand_root,
                )
            conditional_outputs: list[str] = []
            change_type = str(metadata.get("type", "general"))
            if change_type == "ai":
                conditional_outputs.extend(
                    config.get("ai_scenario_required_outputs", [])
                )
            if change_type == "ui":
                conditional_outputs.extend(
                    config.get("prototype_required_outputs", [])
                )
            for relative_path in conditional_outputs:
                artifact = demand_root / relative_path
                if not artifact.is_file():
                    report.add(
                        "missing-conditional-artifact",
                        f"{change_type} change requires {relative_path}.",
                        artifact,
                    )


def _validate_specs(
    project: Path,
    change_root: Path,
    report: ValidationReport,
) -> set[str]:
    active_ids: set[str] = set()
    for spec_path in change_root.glob("specs/**/*.md"):
        text = spec_path.read_text(encoding="utf-8")
        if not DELTA_HEADING.search(text):
            report.add(
                "invalid-delta-heading",
                "Spec must contain ADDED, MODIFIED, or REMOVED Requirements.",
                spec_path,
            )
            continue
        requirements = parse_delta_spec(text)
        if not requirements:
            report.add(
                "missing-requirement",
                "Delta spec contains no valid requirement headings.",
                spec_path,
            )
            continue
        domain = spec_path.parent.name
        baseline_path = project / "specs" / domain / "spec.md"
        baseline = (
            parse_baseline_spec(baseline_path.read_text(encoding="utf-8"))
            if baseline_path.exists()
            else {}
        )
        for requirement in requirements:
            if requirement.operation in {"ADDED", "MODIFIED"}:
                active_ids.add(requirement.requirement_id)
                if not re.search(r"\b(MUST|SHALL|SHOULD|MAY)\b", requirement.content):
                    report.add(
                        "missing-requirement-strength",
                        f"{requirement.requirement_id} needs RFC 2119 behavior language.",
                        spec_path,
                    )
                if not requirement.scenarios:
                    report.add(
                        "missing-scenario",
                        f"{requirement.requirement_id} needs at least one scenario.",
                        spec_path,
                    )
                elif not has_given_when_then(requirement.content):
                    report.add(
                        "invalid-scenario",
                        f"{requirement.requirement_id} scenario needs Given/When/Then.",
                        spec_path,
                    )
            if requirement.operation == "ADDED" and requirement.requirement_id in baseline:
                report.add(
                    "baseline-conflict",
                    f"ADDED requirement already exists: {requirement.requirement_id}",
                    spec_path,
                )
            if requirement.operation in {"MODIFIED", "REMOVED"} and (
                requirement.requirement_id not in baseline
            ):
                report.add(
                    "missing-baseline-requirement",
                    f"{requirement.operation} target does not exist: "
                    f"{requirement.requirement_id}",
                    spec_path,
                )
    return active_ids


def _validate_traceability(
    change_root: Path,
    active_ids: set[str],
    report: ValidationReport,
) -> None:
    acceptance_path = change_root / "acceptance.md"
    tasks_path = change_root / "tasks.md"
    acceptance_ids = (
        requirement_ids(acceptance_path.read_text(encoding="utf-8"))
        if acceptance_path.exists()
        else set()
    )
    task_ids = (
        requirement_ids(tasks_path.read_text(encoding="utf-8"))
        if tasks_path.exists()
        else set()
    )
    for requirement_id in sorted(active_ids):
        if requirement_id not in acceptance_ids:
            report.add(
                "missing-acceptance-trace",
                f"Acceptance criteria do not reference {requirement_id}.",
                acceptance_path,
            )
        if requirement_id not in task_ids:
            report.add(
                "missing-task-trace",
                f"Tasks do not reference {requirement_id}.",
                tasks_path,
            )
    if acceptance_path.exists() and active_ids and not has_given_when_then(
        acceptance_path.read_text(encoding="utf-8")
    ):
        report.add(
            "invalid-acceptance-scenario",
            "Acceptance criteria need Given/When/Then.",
            acceptance_path,
        )


def _validate_approval(
    change_root: Path,
    metadata: dict[str, object],
    report: ValidationReport,
) -> None:
    status = str(metadata.get("status", "draft"))
    if status not in {"approved", "implementing", "verified", "archived"}:
        return
    approval_path = change_root / "approval.md"
    text = approval_path.read_text(encoding="utf-8") if approval_path.exists() else ""
    if (
        "Decision: approved" not in text
        or not metadata.get("approved_by")
        or "Approver: pending" in text
    ):
        report.add(
            "invalid-approval",
            "Approved lifecycle states require a recorded approval.",
            approval_path,
        )


def validate_change(
    project: Path,
    change_id: str,
    strict: bool = False,
) -> ValidationReport:
    project = project.resolve()
    change_root = resolve_change(project, change_id)
    metadata = load_metadata(change_root)
    report = ValidationReport(change_id)

    _required_files(project, change_root, metadata, report)
    _validate_proposal(change_root, report)
    _validate_design(change_root, metadata, report)
    _validate_placeholders(change_root, report, strict)
    active_ids = _validate_specs(project, change_root, report)
    _validate_traceability(change_root, active_ids, report)
    _validate_approval(change_root, metadata, report)
    return report
