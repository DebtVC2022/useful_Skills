import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from demandspec_cli.cli import main
from tests.test_validation import fill_valid_lite_change


class CliTests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            result = main(argv)
        return result, output.getvalue()

    def test_change_commands_create_list_show_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _ = self.run_cli(
                [
                    "change",
                    "new",
                    "客户标签展示",
                    "--domain",
                    "crm",
                    "--project",
                    tmp,
                ]
            )
            self.assertEqual(code, 0)
            change = next(
                item
                for item in (project / "changes").iterdir()
                if item.name != "archive"
            )
            fill_valid_lite_change(change)

            code, listing = self.run_cli(["change", "list", "--project", tmp])
            self.assertEqual(code, 0)
            self.assertIn(change.name, listing)

            code, shown = self.run_cli(
                ["change", "show", change.name, "--project", tmp]
            )
            self.assertEqual(code, 0)
            self.assertIn("客户标签展示", shown)

            code, validation = self.run_cli(
                [
                    "change",
                    "validate",
                    change.name,
                    "--project",
                    tmp,
                    "--strict",
                    "--json",
                ]
            )
            self.assertEqual(code, 0)
            self.assertIn('"valid": true', validation)

    def test_change_status_and_approval_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.run_cli(
                [
                    "change",
                    "new",
                    "客户标签展示",
                    "--domain",
                    "crm",
                    "--project",
                    tmp,
                ]
            )
            change = next(
                item
                for item in (project / "changes").iterdir()
                if item.name != "archive"
            )
            self.assertEqual(
                self.run_cli(
                    [
                        "change",
                        "set-status",
                        change.name,
                        "clarifying",
                        "--project",
                        tmp,
                    ]
                )[0],
                0,
            )
            self.assertEqual(
                self.run_cli(
                    [
                        "change",
                        "set-status",
                        change.name,
                        "review",
                        "--project",
                        tmp,
                    ]
                )[0],
                0,
            )
            self.assertEqual(
                self.run_cli(
                    [
                        "change",
                        "approve",
                        change.name,
                        "--approver",
                        "需求委员会",
                        "--project",
                        tmp,
                    ]
                )[0],
                0,
            )

    def test_legacy_demand_commands_remain_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = self.run_cli(
                ["new", "存量需求", "--project", tmp, "--type", "general"]
            )
            self.assertEqual(code, 0)
            demand_id = next((Path(tmp) / "demands").iterdir()).name
            self.assertEqual(self.run_cli(["status", "--project", tmp])[0], 0)
            self.assertEqual(
                self.run_cli(
                    ["validate", "--project", tmp, "--demand-id", demand_id]
                )[0],
                0,
            )
            self.assertEqual(
                self.run_cli(["archive", demand_id, "--project", tmp])[0],
                0,
            )

    def test_codex_install_includes_prompts_and_discoverable_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            codex_home = Path(tmp) / "codex"
            project.mkdir()
            with patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
                code, _ = self.run_cli(
                    ["install", "codex", "--project", str(project)]
                )

            self.assertEqual(code, 0)
            self.assertTrue(
                (codex_home / "prompts" / "demandspec-intake.md").is_file()
            )
            self.assertTrue(
                (codex_home / "skills" / "demandspec" / "SKILL.md").is_file()
            )


if __name__ == "__main__":
    unittest.main()
