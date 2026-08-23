import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from benchmarks.context_integration.s01_credit_memo.release_bundle import build_release_bundle


class ReleaseBundleTests(unittest.TestCase):
    def test_builds_only_opaque_zip_assets_and_checksums(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            public = root / "public"
            for name in ("job-111111111111", "job-222222222222"):
                d = public / name
                (d / "workspace").mkdir(parents=True)
                (d / "SYSTEM.md").write_text("office assistant\n", encoding="utf-8")
                (d / "WORK_ORDER.md").write_text("process work\n", encoding="utf-8")
                (d / "workspace" / "SOP.html").write_text("<h1>policy</h1>", encoding="utf-8")

            release = root / "release"
            assets = build_release_bundle(public, release)

            self.assertEqual(
                {p.name for p in assets},
                {"job-111111111111.zip", "job-222222222222.zip"},
            )
            self.assertEqual(
                {p.name for p in release.iterdir()},
                {"job-111111111111.zip", "job-222222222222.zip", "SHA256SUMS.txt"},
            )
            with zipfile.ZipFile(release / "job-111111111111.zip") as zf:
                self.assertEqual(
                    set(zf.namelist()),
                    {"SYSTEM.md", "WORK_ORDER.md", "workspace/SOP.html"},
                )

            sums = (release / "SHA256SUMS.txt").read_text(encoding="utf-8")
            for asset in assets:
                digest = hashlib.sha256(asset.read_bytes()).hexdigest()
                self.assertIn(f"{digest}  {asset.name}", sums)

    def test_rejects_non_opaque_public_entry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            public = root / "public"
            public.mkdir()
            (public / "local_A").mkdir()
            with self.assertRaises(ValueError):
                build_release_bundle(public, root / "release")

    def test_rejects_loose_files_in_public_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            public = root / "public"
            public.mkdir()
            (public / "mapping.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_release_bundle(public, root / "release")


if __name__ == "__main__":
    unittest.main()
