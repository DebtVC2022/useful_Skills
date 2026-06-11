import tempfile
import unittest
from pathlib import Path

from demandspec_cli.changes import create_change, load_metadata, save_metadata
from demandspec_cli.validation import validate_change


def fill_valid_lite_change(change: Path) -> None:
    (change / "proposal.md").write_text(
        """# Change Proposal

## Problem
Sales users cannot see customer labels in the visit form.

## Intent
Expose approved labels before a visit is submitted.

## Scope
Display labels in the visit form.

## Non-Goals
Editing labels is excluded.

## Impact
The CRM visit form reads the existing label service.

## Dependencies
Customer label service availability.
""",
        encoding="utf-8",
    )
    metadata = load_metadata(change)
    domain = metadata["domain"]
    (change / "specs" / domain / "spec.md").write_text(
        """# CRM Requirement Delta

## ADDED Requirements

### Requirement: CRM-LABEL-001 Display customer labels
The system MUST display approved customer labels in the visit form.

#### Scenario: Labels are available
- GIVEN a customer has approved labels
- WHEN a sales user opens the visit form
- THEN the approved labels are displayed
""",
        encoding="utf-8",
    )
    (change / "acceptance.md").write_text(
        """# Acceptance Criteria

## Scenarios

### CRM-LABEL-001 Labels are available
- GIVEN a customer has approved labels
- WHEN a sales user opens the visit form
- THEN the approved labels are displayed
""",
        encoding="utf-8",
    )
    (change / "tasks.md").write_text(
        """# Implementation Tasks

## Tasks

- [ ] CRM-LABEL-001 Read approved labels
- [ ] CRM-LABEL-001 Render labels in the visit form
""",
        encoding="utf-8",
    )


class ValidationTests(unittest.TestCase):
    def test_empty_generated_change_fails_strict_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "客户标签展示", domain="crm")

            report = validate_change(project, change.name, strict=True)

            self.assertFalse(report.valid)
            self.assertIn("placeholder-content", {issue.code for issue in report.issues})

    def test_valid_lite_change_passes_strict_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "客户标签展示", domain="crm")
            fill_valid_lite_change(change)

            report = validate_change(project, change.name, strict=True)

            self.assertTrue(report.valid, report.format_text())

    def test_missing_acceptance_and_task_traceability_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "客户标签展示", domain="crm")
            fill_valid_lite_change(change)
            (change / "acceptance.md").write_text(
                "# Acceptance Criteria\n\n## Scenarios\n\nNo linked scenario.\n",
                encoding="utf-8",
            )

            report = validate_change(project, change.name, strict=True)

            codes = {issue.code for issue in report.issues}
            self.assertIn("missing-acceptance-trace", codes)

    def test_modified_requirement_must_exist_in_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "修改客户标签", domain="crm")
            fill_valid_lite_change(change)
            spec = change / "specs" / "crm" / "spec.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "## ADDED Requirements", "## MODIFIED Requirements"
                ),
                encoding="utf-8",
            )

            report = validate_change(project, change.name, strict=True)

            self.assertIn(
                "missing-baseline-requirement",
                {issue.code for issue in report.issues},
            )

    def test_full_profile_requires_linked_demand_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(
                project,
                "客户意图识别",
                domain="crm",
                change_type="ai",
            )
            fill_valid_lite_change(change)
            metadata = load_metadata(change)
            demand = project / "demands" / metadata["demand_id"]
            for child in sorted(demand.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            demand.rmdir()

            report = validate_change(project, change.name, strict=True)

            self.assertIn(
                "missing-demand-package",
                {issue.code for issue in report.issues},
            )

    def test_ai_change_requires_configured_conditional_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(
                project,
                "客户意图识别",
                domain="crm",
                change_type="ai",
            )
            fill_valid_lite_change(change)

            report = validate_change(project, change.name, strict=True)

            self.assertIn(
                "missing-conditional-artifact",
                {issue.code for issue in report.issues},
            )

    def test_full_profile_design_sections_must_be_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(
                project,
                "客户意图识别",
                domain="crm",
                change_type="ai",
            )
            fill_valid_lite_change(change)
            metadata = load_metadata(change)
            demand = project / "demands" / metadata["demand_id"]
            algorithm = demand / "07_handoff" / "algorithm-tasks.md"
            algorithm.write_text("# 算法任务\n\n- CRM-AI-001 实现意图识别。\n", encoding="utf-8")

            report = validate_change(project, change.name, strict=True)

            self.assertIn("empty-design-section", {issue.code for issue in report.issues})

    def test_approved_status_requires_approval_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "客户标签展示", domain="crm")
            fill_valid_lite_change(change)
            metadata = load_metadata(change)
            metadata["status"] = "approved"
            save_metadata(change, metadata)

            report = validate_change(project, change.name, strict=True)

            self.assertIn("invalid-approval", {issue.code for issue in report.issues})


if __name__ == "__main__":
    unittest.main()
