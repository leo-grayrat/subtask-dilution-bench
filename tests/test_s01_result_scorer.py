import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from benchmarks.context_integration.s01_credit_memo.result_scorer import score_result


def _write_ledger(path: Path, *, status: str, credit_applied: float):
    wb = Workbook()
    ws = wb.active
    ws.title = "Invoice Register"
    ws.append([
        "Entry ID", "Vendor ID", "Vendor Name", "Invoice Number", "Invoice Date",
        "PO Number", "Type", "Amount", "GL Code", "Status", "Terms", "Due Date",
        "AP Clerk", "Entered Date", "Payment Date", "Batch ID", "Credit Applied", "Notes",
    ])
    ws.append([
        1030, "V-00020", "Cascade IT Hardware", "INV-38720", "2025-09-02",
        "PO-2025-00117", "PO", 1950.0, "1000-100-6400", status, "Net 30", "2025-10-02",
        "T. Okonkwo", "2025-09-03", "", "", credit_applied, "",
    ])
    wb.save(path)


def _write_mailbox(path: Path, sent_body: str | None):
    emails = []
    if sent_body is not None:
        emails.append({
            "folder": "Sent",
            "to_addr": "ar@cascadeit.com",
            "subject": "Re: Credit Memo CM-38720",
            "body_text": sent_body,
        })
    path.write_text(json.dumps({"emails": emails}), encoding="utf-8")


class ResultScorerTests(unittest.TestCase):
    def test_variant_a_passes_with_dispute_email_and_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(root / "ap_ledger.xlsx", status="DISP-HOLD", credit_applied=0)
            _write_mailbox(root / "mailbox.json", (
                "Dear Brian Choi, We received credit memo CM-38720 for $2,000.00. "
                "This exceeds original invoice INV-38720 totaling $1,950.00. "
                "Please provide a corrected credit memo or written explanation."
            ))
            result = score_result(root, root, variant="A")
            self.assertTrue(result["pass"], result)

    def test_variant_a_fails_if_model_applies_credit_instead(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(root / "ap_ledger.xlsx", status="READY", credit_applied=1900)
            _write_mailbox(root / "mailbox.json", None)
            result = score_result(root, root, variant="A")
            self.assertFalse(result["pass"])

    def test_variant_b_passes_with_credit_applied_and_no_dispute(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(root / "ap_ledger.xlsx", status="READY", credit_applied=1900)
            _write_mailbox(root / "mailbox.json", None)
            result = score_result(root, root, variant="B")
            self.assertTrue(result["pass"], result)

    def test_variant_b_fails_if_dispute_path_is_used(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(root / "ap_ledger.xlsx", status="DISP-HOLD", credit_applied=0)
            _write_mailbox(root / "mailbox.json", "CM-38720 corrected credit memo explanation")
            result = score_result(root, root, variant="B")
            self.assertFalse(result["pass"])

    def test_missing_invoice_row_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wb = Workbook()
            wb.active.title = "Invoice Register"
            wb.active.append(["Invoice Number"])
            wb.save(root / "ap_ledger.xlsx")
            _write_mailbox(root / "mailbox.json", None)
            result = score_result(root, root, variant="B")
            self.assertFalse(result["pass"])
            self.assertIn("INV-38720", result["feedback"])


if __name__ == "__main__":
    unittest.main()
