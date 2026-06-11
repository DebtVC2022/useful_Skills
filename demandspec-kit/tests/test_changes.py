import tempfile
import unittest
from pathlib import Path

from demandspec_cli.changes import (
    approve_change,
    create_change,
    load_metadata,
    set_change_status,
)


class ChangeModelTests(unittest.TestCase):
    def test_lite_change_creates_required_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(
                project,
                "客户标签展示",
                domain="crm",
                owner="产品团队",
            )

            self.assertTrue((project / "specs").is_dir())
            self.assertTrue((project / "changes" / "archive").is_dir())
            self.assertTrue((change / "proposal.md").is_file())
            self.assertTrue((change / "specs" / "crm" / "spec.md").is_file())
            self.assertTrue((change / "acceptance.md").is_file())
            self.assertTrue((change / "tasks.md").is_file())
            self.assertTrue((change / "approval.md").is_file())
            self.assertFalse((change / "design.md").exists())
            self.assertEqual(load_metadata(change)["profile"], "lite")

    def test_ai_change_automatically_uses_full_profile_and_links_demand(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(
                project,
                "客户意图识别",
                domain="crm",
                change_type="ai",
            )
            metadata = load_metadata(change)

            self.assertEqual(metadata["profile"], "full")
            self.assertTrue((change / "design.md").is_file())
            self.assertTrue(
                (project / "demands" / metadata["demand_id"] / "00_intake").is_dir()
            )

    def test_lifecycle_requires_sequential_transitions_and_review_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            change = create_change(project, "客户标签展示", domain="crm")
            change_id = change.name

            with self.assertRaises(ValueError):
                set_change_status(project, change_id, "approved")

            set_change_status(project, change_id, "clarifying")
            set_change_status(project, change_id, "review")
            with self.assertRaises(ValueError):
                set_change_status(project, change_id, "approved")
            approve_change(project, change_id, approver="需求委员会")

            metadata = load_metadata(change)
            self.assertEqual(metadata["status"], "approved")
            approval = (change / "approval.md").read_text(encoding="utf-8")
            self.assertIn("需求委员会", approval)
            self.assertIn("approved", approval)

            set_change_status(project, change_id, "implementing")
            set_change_status(project, change_id, "verified")
            with self.assertRaises(ValueError):
                set_change_status(project, change_id, "archived")


if __name__ == "__main__":
    unittest.main()
