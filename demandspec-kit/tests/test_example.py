import shutil
import tempfile
import unittest
from pathlib import Path

from demandspec_cli.cli import init_project
from demandspec_cli.validation import validate_change


class ExampleTests(unittest.TestCase):
    def test_visit_form_example_passes_strict_change_validation(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "examples"
            / "visit-form-auto-generation"
        )
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_project(project)
            demand = project / "demands" / "visit-form-auto-generation"
            demand.mkdir(parents=True)
            for stage in source.iterdir():
                if stage.name == "change":
                    continue
                if stage.is_dir():
                    shutil.copytree(stage, demand / stage.name)
            shutil.copytree(
                source / "change",
                project / "changes" / "visit-form-auto-generation",
            )

            report = validate_change(
                project,
                "visit-form-auto-generation",
                strict=True,
            )

            self.assertTrue(report.valid, report.format_text())


if __name__ == "__main__":
    unittest.main()
