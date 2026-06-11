import tempfile
import unittest
from pathlib import Path

from demandspec_cli.resource_access import resource_path


class ResourceTests(unittest.TestCase):
    def test_runtime_resources_are_available_inside_package(self):
        self.assertTrue(resource_path("configs", "config.yaml").is_file())
        self.assertTrue(resource_path("templates", "prd.md").is_file())
        self.assertTrue(
            resource_path("commands", "codex", "demandspec-intake.md").is_file()
        )
        self.assertTrue(resource_path("skills", "demandspec", "SKILL.md").is_file())

    def test_project_can_initialize_from_packaged_resources(self):
        from demandspec_cli.cli import init_project

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_project(project)

            self.assertTrue((project / ".demandspec" / "config.yaml").is_file())
            self.assertTrue((project / ".demandspec" / "templates" / "prd.md").is_file())
            self.assertTrue((project / "specs").is_dir())
            self.assertTrue((project / "changes" / "archive").is_dir())


if __name__ == "__main__":
    unittest.main()
