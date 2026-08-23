import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmarks.context_integration.s01_credit_memo.blind_export import LeakageError, export_one, export_variants


def _make_variant(root: Path, name: str, *, instruction: str = "Process the unread work according to policy.\n") -> Path:
    task = root / name
    (task / "environment/initial_workspace").mkdir(parents=True)
    (task / "environment/initial_external_services/google_mail").mkdir(parents=True)
    (task / "tests").mkdir()
    (task / "instruction.md").write_text(instruction, encoding="utf-8")
    (task / "system_prompt.md").write_text("You are an office assistant.\n", encoding="utf-8")
    (task / "task.toml").write_text(f'name = "{name}"\n', encoding="utf-8")
    (task / "environment/initial_workspace/SOP.html").write_text("<h1>Company policy</h1>", encoding="utf-8")
    (task / "environment/initial_external_services/google_mail/inbox.json").write_text('{"emails": []}\n', encoding="utf-8")
    (task / "tests/rubrics.json").write_text('{"secret": "correct answer"}\n', encoding="utf-8")
    (task / "tests/scorer.py").write_text("# secret answer\n", encoding="utf-8")
    return task


class BlindExportTests(unittest.TestCase):
    def test_export_one_contains_only_model_visible_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = _make_variant(base / "generated", "local_A")
            public = base / "public"
            package = export_one(source, public, run_id="job-0123456789ab")
            self.assertEqual({p.name for p in package.iterdir()}, {"SYSTEM.md", "WORK_ORDER.md", "workspace", "services"})
            self.assertFalse((package / "tests").exists())
            self.assertFalse((package / "task.toml").exists())
            combined = "\n".join(p.read_text(encoding="utf-8") for p in package.rglob("*") if p.is_file() and p.suffix in {".md", ".json", ".html"})
            self.assertNotIn("correct answer", combined)

    def test_export_variants_uses_opaque_names_and_private_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            generated = base / "generated"
            for name in ("local_A", "local_B", "full_A", "full_B"):
                _make_variant(generated, name)
            public = base / "public"
            manifest = base / "private" / "mapping.json"
            tokens = ["111111111111", "222222222222", "333333333333", "444444444444"]
            with patch("benchmarks.context_integration.s01_credit_memo.blind_export.secrets.token_hex", side_effect=tokens):
                exported = export_variants(generated, public, manifest)
            self.assertEqual(len(exported), 4)
            self.assertEqual({p.name for p in public.iterdir()}, {f"job-{t}" for t in tokens})
            for name in (p.name.lower() for p in public.iterdir()):
                self.assertNotIn("local", name)
                self.assertNotIn("full", name)
                self.assertNotIn("variant", name)
            mapping = json.loads(manifest.read_text(encoding="utf-8"))["runs"]
            self.assertEqual({v["condition"] for v in mapping.values()}, {"local_A", "local_B", "full_A", "full_B"})
            self.assertFalse(manifest.is_relative_to(public))

    def test_manifest_cannot_be_inside_public_root(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            generated = base / "generated"
            for name in ("local_A", "local_B", "full_A", "full_B"):
                _make_variant(generated, name)
            public = base / "public"
            with self.assertRaises(ValueError):
                export_variants(generated, public, public / "mapping.json")

    def test_leak_marker_in_model_visible_text_is_rejected_and_cleaned_up(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = _make_variant(base / "generated", "local_A", instruction="This is S01_credit_memo benchmark.\n")
            public = base / "public"
            with self.assertRaises(LeakageError):
                export_one(source, public, run_id="job-0123456789ab")
            self.assertFalse((public / "job-0123456789ab").exists())


if __name__ == "__main__":
    unittest.main()
