import tempfile
import unittest
from pathlib import Path

from demandspec_cli.cli import new_demand, slugify


class IdentifierTests(unittest.TestCase):
    def test_distinct_chinese_names_get_distinct_stable_slugs(self):
        first = slugify("客户画像需求")
        second = slugify("额度调整需求")

        self.assertNotEqual(first, second)
        self.assertEqual(first, slugify("客户画像需求"))
        self.assertRegex(first, r"^demand-[a-f0-9]{8}$")

    def test_existing_demand_is_not_silently_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            new_demand(project, "客户画像需求")

            with self.assertRaises(FileExistsError):
                new_demand(project, "客户画像需求")


if __name__ == "__main__":
    unittest.main()
