import os
import tempfile
import unittest
from pathlib import Path

from tests.test_s01_handbook_materialize import _make_source
from benchmarks.context_integration.s01_credit_memo.run import prepare_variants, harbor_command


class S01RunnerTests(unittest.TestCase):
    def test_prepare_variants_builds_all_four_tasks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = root / "handbook"
            source = handbook / "tasks/finance_meridian_partners_158b9045"
            _make_source(source)
            out = root / "generated"

            variants = prepare_variants(handbook, out)

            self.assertEqual(set(variants), {"local_A", "local_B", "full_A", "full_B"})
            for path in variants.values():
                self.assertTrue((path / "instruction.md").exists())
                self.assertTrue((path / "tests/rubrics.json").exists())

    def test_harbor_command_matches_current_platform(self):
        handbook = Path("/tmp/handbook")
        task = Path("/tmp/generated/local_A")
        env_file = Path("/tmp/handbook/.env")
        cmd = harbor_command(handbook, task, model="openai/example", env_file=env_file)
        harbor_path = handbook / (".venv/Scripts/harbor.exe" if os.name == "nt" else ".venv/bin/harbor")
        self.assertEqual(cmd[0], str(harbor_path))
        self.assertEqual(cmd[1:4], ["run", "-p", str(task)])
        self.assertIn("agent_harness.openhands_agent:OpenHandsAgent", cmd)
        self.assertIn("openai/example", cmd)
        self.assertEqual(cmd[-2:], ["--env-file", str(env_file)])

    def test_runner_can_be_executed_directly_in_prepare_only_mode(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = root / "handbook"
            source = handbook / "tasks/finance_meridian_partners_158b9045"
            _make_source(source)
            out = root / "generated"
            script = Path(__file__).parents[1] / "benchmarks/context_integration/s01_credit_memo/run.py"
            result = subprocess.run([
                sys.executable, str(script),
                "--handbook", str(handbook),
                "--output", str(out),
                "--prepare-only",
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / "local_A/tests/rubrics.json").exists())
            self.assertTrue((out / "full_B/tests/rubrics.json").exists())


if __name__ == "__main__":
    unittest.main()
