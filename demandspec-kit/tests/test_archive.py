import tempfile
import unittest
from pathlib import Path

from demandspec_cli.archive import ArchiveError, archive_change
from demandspec_cli.changes import (
    approve_change,
    create_change,
    set_change_status,
)
from tests.test_validation import fill_valid_lite_change


def make_verified(project: Path, change: Path) -> None:
    change_id = change.name
    set_change_status(project, change_id, "clarifying")
    set_change_status(project, change_id, "review")
    approve_change(project, change_id, approver="需求委员会")
    set_change_status(project, change_id, "implementing")
    set_change_status(project, change_id, "verified")
    tasks = change / "tasks.md"
    tasks.write_text(
        tasks.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
        encoding="utf-8",
    )


class ArchiveTests(unittest.TestCase):
    def test_archive_rejects_draft_and_incomplete_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "客户标签展示", domain="crm")
            fill_valid_lite_change(change)

            with self.assertRaises(ArchiveError):
                archive_change(project, change.name)

            change_id = change.name
            set_change_status(project, change_id, "clarifying")
            set_change_status(project, change_id, "review")
            approve_change(project, change_id, approver="需求委员会")
            set_change_status(project, change_id, "implementing")
            set_change_status(project, change_id, "verified")

            with self.assertRaises(ArchiveError):
                archive_change(project, change.name)

    def test_archive_merges_added_modified_and_removed_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)

            added = create_change(project, "新增客户标签", domain="crm")
            fill_valid_lite_change(added)
            (added / "specs" / "crm" / "notes.md").write_text(
                """# CRM Requirement Delta

## ADDED Requirements

### Requirement: CRM-NOTE-001 Display visit notes
The system MUST display approved visit notes in the visit form.

#### Scenario: Notes are available
- GIVEN a customer has approved visit notes
- WHEN a sales user opens the visit form
- THEN the approved visit notes are displayed
""",
                encoding="utf-8",
            )
            with (added / "acceptance.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n### CRM-NOTE-001 Notes are available\n"
                    "- GIVEN approved visit notes exist\n"
                    "- WHEN the visit form opens\n"
                    "- THEN the notes are displayed\n"
                )
            with (added / "tasks.md").open("a", encoding="utf-8") as handle:
                handle.write("\n- [ ] CRM-NOTE-001 Render approved visit notes\n")
            make_verified(project, added)
            added_archive = archive_change(project, added.name)
            baseline = project / "specs" / "crm" / "spec.md"
            added_baseline = baseline.read_text(encoding="utf-8")
            self.assertIn("CRM-LABEL-001", added_baseline)
            self.assertIn("CRM-NOTE-001", added_baseline)
            self.assertTrue(added_archive.is_dir())
            self.assertFalse(added.exists())

            modified = create_change(project, "调整客户标签", domain="crm")
            fill_valid_lite_change(modified)
            spec = modified / "specs" / "crm" / "spec.md"
            spec.write_text(
                spec.read_text(encoding="utf-8")
                .replace("## ADDED Requirements", "## MODIFIED Requirements")
                .replace(
                    "display approved customer labels",
                    "display prioritized customer labels",
                ),
                encoding="utf-8",
            )
            make_verified(project, modified)
            archive_change(project, modified.name)
            baseline_text = baseline.read_text(encoding="utf-8")
            self.assertIn("display prioritized customer labels", baseline_text)
            self.assertNotIn("display approved customer labels", baseline_text)

            removed = create_change(project, "移除客户标签", domain="crm")
            fill_valid_lite_change(removed)
            (removed / "specs" / "crm" / "spec.md").write_text(
                """# CRM Requirement Delta

## REMOVED Requirements

### Requirement: CRM-LABEL-001 Display customer labels
Removed because the visit form now uses a consolidated customer summary.
""",
                encoding="utf-8",
            )
            make_verified(project, removed)
            archive_change(project, removed.name)
            self.assertNotIn("CRM-LABEL-001", baseline.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
