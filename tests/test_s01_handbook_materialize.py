import base64
import json
import tempfile
import unittest
import zlib
from pathlib import Path

from benchmarks.context_integration.s01_credit_memo.materialize import materialize, _decode_ascii85_flate_stream


def _pdf_with_text(text: str, *, newline_before_endstream: bool = True) -> bytes:
    raw = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    encoded = base64.a85encode(zlib.compress(raw), adobe=True)[2:]
    stream_end = b"\nendstream\n" if newline_before_endstream else b"endstream\n"
    obj1 = b"1 0 obj\n<< /Length " + str(len(encoded)).encode() + b" /Filter [ /ASCII85Decode /FlateDecode ] >>\nstream\n" + encoded + stream_end + b"endobj\n"
    obj2 = b"2 0 obj\n<< /Type /Catalog >>\nendobj\n"
    prefix = b"%PDF-1.4\n" + obj1 + obj2
    offsets = {int(m.group(1)): m.start() for m in __import__('re').finditer(rb'(?m)^(\d+) 0 obj\b', prefix)}
    xref_at = len(prefix)
    xref = b"xref\n0 3\n0000000000 65535 f \n" + f"{offsets[1]:010d} 00000 n \n{offsets[2]:010d} 00000 n \n".encode()
    trailer = b"trailer\n<< /Size 3 /Root 2 0 R >>\nstartxref\n" + str(xref_at).encode() + b"\n%%EOF\n"
    return prefix + xref + trailer


def _make_source(root: Path):
    (root / "environment/initial_external_services/google_mail").mkdir(parents=True)
    (root / "environment/initial_workspace").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "instruction.md").write_text("Process all unread emails according to the SOP.\n", encoding="utf-8")
    (root / "environment/initial_workspace/keep.txt").write_text("keep me", encoding="utf-8")
    pdf = _pdf_with_text("Credit Memo CM-38720 Amount $2,000.00")
    inbox = {
        "emails": [
            {"email_id": "8", "subject": "Invoice INV-38720", "body_text": "Total $1,950.00", "is_read": True, "attachments": []},
            {"email_id": "63", "subject": "Credit Memo CM-38720", "body_text": "amount $2,000.00; Credit Amount: $2,000.00", "is_read": False,
             "attachments": [{"filename": "CM-38720.pdf", "content_type": "application/pdf", "content_base64": base64.b64encode(pdf).decode()}]},
            {"email_id": "70", "subject": "Other unread work", "body_text": "unrelated", "is_read": False, "attachments": []},
        ]
    }
    (root / "environment/initial_external_services/google_mail/inbox.json").write_text(json.dumps(inbox, indent=2), encoding="utf-8")
    rubrics = [
        {"id": "background", "sort_order": 0, "rubric_text": "background", "verifier_code": "def verify(workspace_path, external_services_path=None): return {\"pass\": True}"},
        {"id": "78ef4e7c-fe51-4573-b827-3ce3baea02ea", "sort_order": 3, "rubric_text": "A dispute email", "verifier_code": "ORIGINAL_EMAIL_A"},
        {"id": "rubric_1775876463672", "sort_order": 13, "rubric_text": "A ledger hold", "verifier_code": "ORIGINAL_LEDGER_A"},
    ]
    (root / "tests/rubrics.json").write_text(json.dumps(rubrics, indent=2), encoding="utf-8")


class MaterializeS01Tests(unittest.TestCase):
    def test_local_a_narrows_workload_but_keeps_source_files(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)
            materialize(src, out, mode="local", variant="A")
            self.assertEqual((out / "environment/initial_workspace/keep.txt").read_text(), "keep me")
            instruction = (out / "instruction.md").read_text()
            self.assertIn("CM-38720", instruction)
            inbox = json.loads((out / "environment/initial_external_services/google_mail/inbox.json").read_text())
            by_id = {e["email_id"]: e for e in inbox["emails"]}
            self.assertFalse(by_id["63"]["is_read"])
            self.assertTrue(by_id["70"]["is_read"])
            self.assertEqual(by_id["63"]["body_text"].count("$2,000.00"), 2)

    def test_full_a_preserves_original_instruction_and_read_states(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)
            materialize(src, out, mode="full", variant="A")
            self.assertEqual((out / "instruction.md").read_text(), "Process all unread emails according to the SOP.\n")
            inbox = json.loads((out / "environment/initial_external_services/google_mail/inbox.json").read_text())
            by_id = {e["email_id"]: e for e in inbox["emails"]}
            self.assertFalse(by_id["70"]["is_read"])

    def test_variant_b_changes_only_target_business_amount_representations(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)
            materialize(src, out, mode="full", variant="B")
            inbox = json.loads((out / "environment/initial_external_services/google_mail/inbox.json").read_text())
            by_id = {e["email_id"]: e for e in inbox["emails"]}
            self.assertEqual(by_id["8"]["body_text"], "Total $1,950.00")
            self.assertNotIn("$2,000.00", by_id["63"]["body_text"])
            self.assertEqual(by_id["63"]["body_text"].count("$1,900.00"), 2)
            pdf = base64.b64decode(by_id["63"]["attachments"][0]["content_base64"])
            decoded = _decode_ascii85_flate_stream(pdf)
            self.assertIn(b"$1,900.00", decoded)
            self.assertNotIn(b"$2,000.00", decoded)

    def test_variant_b_rewrites_reportlab_stream_without_newline_before_endstream(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)
            inbox_path = src / "environment/initial_external_services/google_mail/inbox.json"
            inbox = json.loads(inbox_path.read_text())
            target = next(e for e in inbox["emails"] if e["email_id"] == "63")
            pdf = _pdf_with_text(
                "Credit Memo CM-38720 Amount $2,000.00",
                newline_before_endstream=False,
            )
            target["attachments"][0]["content_base64"] = base64.b64encode(pdf).decode()
            inbox_path.write_text(json.dumps(inbox, indent=2), encoding="utf-8")

            materialize(src, out, mode="full", variant="B")

            output_inbox = json.loads(
                (out / "environment/initial_external_services/google_mail/inbox.json").read_text()
            )
            output_target = next(e for e in output_inbox["emails"] if e["email_id"] == "63")
            output_pdf = base64.b64decode(output_target["attachments"][0]["content_base64"])
            decoded = _decode_ascii85_flate_stream(output_pdf)
            self.assertIn(b"$1,900.00", decoded)
            self.assertNotIn(b"$2,000.00", decoded)

    def test_invalid_mode_or_variant_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            _make_source(src)
            with self.assertRaises(ValueError):
                materialize(src, Path(td) / "x", mode="tiny", variant="A")
            with self.assertRaises(ValueError):
                materialize(src, Path(td) / "y", mode="full", variant="C")

    def test_missing_target_email_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)
            p = src / "environment/initial_external_services/google_mail/inbox.json"
            data = json.loads(p.read_text())
            data["emails"] = [e for e in data["emails"] if e["email_id"] != "63"]
            p.write_text(json.dumps(data))
            with self.assertRaises(RuntimeError):
                materialize(src, out, mode="full", variant="A")

    def test_local_uses_only_target_rubrics_and_full_b_rewrites_only_target_rubrics(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)

            local_b = base / "local_b"
            materialize(src, local_b, mode="local", variant="B")
            local_rubrics = json.loads((local_b / "tests/rubrics.json").read_text())
            self.assertEqual(
                {r["id"] for r in local_rubrics},
                {"78ef4e7c-fe51-4573-b827-3ce3baea02ea", "rubric_1775876463672"},
            )
            self.assertTrue(all("variant B" in r["rubric_text"] for r in local_rubrics))

            full_b = base / "full_b"
            materialize(src, full_b, mode="full", variant="B")
            full_rubrics = json.loads((full_b / "tests/rubrics.json").read_text())
            by_id = {r["id"]: r for r in full_rubrics}
            self.assertEqual(by_id["background"]["rubric_text"], "background")
            self.assertEqual(by_id["background"]["verifier_code"], 'def verify(workspace_path, external_services_path=None): return {"pass": True}')
            self.assertIn("variant B", by_id["78ef4e7c-fe51-4573-b827-3ce3baea02ea"]["rubric_text"])
            self.assertIn("variant B", by_id["rubric_1775876463672"]["rubric_text"])

            full_a = base / "full_a"
            materialize(src, full_a, mode="full", variant="A")
            full_a_rubrics = json.loads((full_a / "tests/rubrics.json").read_text())
            self.assertEqual(full_a_rubrics[1]["verifier_code"], "ORIGINAL_EMAIL_A")
            self.assertEqual(full_a_rubrics[2]["verifier_code"], "ORIGINAL_LEDGER_A")

    def test_cli_materializes_requested_case(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)
            result = subprocess.run([
                sys.executable,
                str(Path(__file__).parents[1] / "benchmarks/context_integration/s01_credit_memo/materialize.py"),
                str(src), str(out), "--mode", "local", "--variant", "B"
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            inbox = json.loads((out / "environment/initial_external_services/google_mail/inbox.json").read_text())
            target = next(e for e in inbox["emails"] if e["email_id"] == "63")
            self.assertIn("$1,900.00", target["body_text"])


if __name__ == "__main__":
    unittest.main()
