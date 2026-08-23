import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmarks.context_integration.s08_expired_agreement.run import SOURCE_TASK, prepare_variants


class S08RunnerTests(unittest.TestCase):
    def test_prepare_variants_builds_all_four_conditions(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            handbook = base / "handbook"
            (handbook / "tasks" / SOURCE_TASK).mkdir(parents=True)
            output = base / "output"

            with patch("benchmarks.context_integration.s08_expired_agreement.run.materialize") as materialize:
                variants = prepare_variants(handbook, output)

            self.assertEqual(set(variants), {"local_A", "local_B", "full_A", "full_B"})
            self.assertEqual(materialize.call_count, 4)
            calls = {(call.kwargs["mode"], call.kwargs["variant"]) for call in materialize.call_args_list}
            self.assertEqual(calls, {("local", "A"), ("local", "B"), ("full", "A"), ("full", "B")})


if __name__ == "__main__":
    unittest.main()
