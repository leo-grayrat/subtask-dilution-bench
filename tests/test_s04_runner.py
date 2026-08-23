import tempfile
import unittest
from pathlib import Path

from tests.test_s04_handbook_materialize import _make_source
from benchmarks.context_integration.s04_contact_history.run import prepare_variants


class S04RunnerTests(unittest.TestCase):
    def test_prepare_variants_builds_all_four_tasks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = root / "handbook"
            _make_source(handbook / "tasks/medical_careig_specialty_pharmacy_f5947c33")
            variants = prepare_variants(handbook, root / "generated")
            self.assertEqual(set(variants), {"local_A", "local_B", "full_A", "full_B"})
            self.assertTrue(all((p / "tests/rubrics.json").exists() for p in variants.values()))


if __name__ == "__main__":
    unittest.main()
