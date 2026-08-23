import tempfile
import unittest
from pathlib import Path

from tests.test_s02_handbook_materialize import _make_source
from benchmarks.context_integration.s02_manager_approval.run import prepare_variants


class S02RunnerTests(unittest.TestCase):
    def test_prepare_variants_builds_all_four_tasks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = root / "handbook"
            source = handbook / "tasks/insurance_vanguard_shield_mutual_9b2f7a29"
            _make_source(source)

            variants = prepare_variants(handbook, root / "generated")

            self.assertEqual(set(variants), {"local_A", "local_B", "full_A", "full_B"})
            for path in variants.values():
                self.assertTrue((path / "instruction.md").exists())
                self.assertTrue((path / "tests/rubrics.json").exists())


if __name__ == "__main__":
    unittest.main()
