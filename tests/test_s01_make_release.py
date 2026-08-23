import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from benchmarks.context_integration.s01_credit_memo.make_release import build_release
from tests.test_s01_handbook_materialize import _make_source


class MakeReleaseTests(unittest.TestCase):
    def test_build_release_keeps_private_mapping_outside_public_assets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = root / "handbook"
            source = handbook / "tasks/finance_meridian_partners_158b9045"
            _make_source(source)
            (source / "system_prompt.md").write_text("You are an office assistant.\n", encoding="utf-8")

            release = root / "release"
            private_manifest = root / "private" / "mapping.json"
            assets = build_release(handbook, release, private_manifest)

            self.assertEqual(len(assets), 4)
            self.assertEqual(len(list(release.glob("job-*.zip"))), 4)
            self.assertTrue((release / "SHA256SUMS.txt").is_file())
            self.assertFalse((release / "mapping.json").exists())

            mapping = json.loads(private_manifest.read_text(encoding="utf-8"))["release_files"]
            self.assertEqual(set(mapping.values()), {"local_A", "local_B", "full_A", "full_B"})
            self.assertEqual(set(mapping), {p.name for p in assets})

            for asset in assets:
                self.assertNotIn("local", asset.name.lower())
                self.assertNotIn("full", asset.name.lower())
                with zipfile.ZipFile(asset) as zf:
                    names = set(zf.namelist())
                    self.assertIn("SYSTEM.md", names)
                    self.assertIn("WORK_ORDER.md", names)
                    self.assertFalse(any(name.startswith("tests/") for name in names))
                    self.assertNotIn("task.toml", names)

    def test_private_manifest_inside_release_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = root / "handbook"
            source = handbook / "tasks/finance_meridian_partners_158b9045"
            _make_source(source)
            (source / "system_prompt.md").write_text("You are an office assistant.\n", encoding="utf-8")
            release = root / "release"
            with self.assertRaises(ValueError):
                build_release(handbook, release, release / "mapping.json")


if __name__ == "__main__":
    unittest.main()
