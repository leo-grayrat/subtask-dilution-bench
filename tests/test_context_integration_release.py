import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from benchmarks.context_integration.make_release import build_release
from benchmarks.context_integration.s01_credit_memo.blind_export import LeakageError, export_one


def _mock_builder(sample: str):
    def build(handbook: Path, output: Path) -> dict[str, Path]:
        variants = {}
        for condition in ("local_A", "local_B", "full_A", "full_B"):
            task = output / condition
            (task / "environment/initial_workspace").mkdir(parents=True)
            (task / "environment/initial_external_services/service").mkdir(parents=True)
            (task / "tests").mkdir()
            (task / "system_prompt.md").write_text("You are an office assistant.\n", encoding="utf-8")
            (task / "instruction.md").write_text(f"Complete the {sample} work order.\n", encoding="utf-8")
            (task / "environment/initial_workspace/input.txt").write_text("visible", encoding="utf-8")
            (task / "environment/initial_external_services/service/state.json").write_text("{}\n", encoding="utf-8")
            (task / "tests/rubrics.json").write_text('{"secret": "answer"}\n', encoding="utf-8")
            variants[condition] = task
        return variants
    return build


class ContextIntegrationReleaseTests(unittest.TestCase):
    def test_build_release_anonymizes_multiple_samples_and_keeps_mapping_private(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            release = root / "release"
            manifest = root / "private/mapping.json"
            builders = {
                "approval_identity": _mock_builder("approval"),
                "contact_history": _mock_builder("contact"),
            }

            with patch("benchmarks.context_integration.make_release.SAMPLE_BUILDERS", builders):
                assets = build_release(root / "handbook", release, manifest)

            self.assertEqual(len(assets), 8)
            self.assertEqual(len(list(release.glob("job-*.zip"))), 8)
            self.assertTrue((release / "SHA256SUMS.txt").is_file())
            self.assertFalse((release / "mapping.json").exists())
            mapping = json.loads(manifest.read_text(encoding="utf-8"))["release_files"]
            self.assertEqual(set(mapping), {asset.name for asset in assets})
            self.assertEqual({record["sample"] for record in mapping.values()}, set(builders))
            self.assertEqual(
                {record["condition"] for record in mapping.values()},
                {"local_A", "local_B", "full_A", "full_B"},
            )
            for asset in assets:
                with zipfile.ZipFile(asset) as archive:
                    names = set(archive.namelist())
                    self.assertEqual(
                        {name.split("/", 1)[0] for name in names},
                        {"SYSTEM.md", "WORK_ORDER.md", "workspace", "services"},
                    )
                    self.assertFalse(any(name.startswith("tests/") for name in names))

    def test_private_manifest_inside_release_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                build_release(root / "handbook", root / "release", root / "release/mapping.json")

    def test_public_export_rejects_plain_benchmark_disclosure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task = root / "task"
            (task / "environment/initial_workspace").mkdir(parents=True)
            (task / "environment/initial_external_services").mkdir(parents=True)
            (task / "system_prompt.md").write_text("You are an assistant.\n", encoding="utf-8")
            (task / "instruction.md").write_text("This is a benchmark task.\n", encoding="utf-8")
            with self.assertRaises(LeakageError):
                export_one(task, root / "public", run_id="job-0123456789ab")


if __name__ == "__main__":
    unittest.main()
