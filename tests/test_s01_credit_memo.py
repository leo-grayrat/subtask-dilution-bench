import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.context_integration.s01_credit_memo.scorer import expected_route, score_result


def test_credit_above_invoice_requires_dispute():
    assert expected_route(invoice_amount=1950, credit_amount=2000) == "dispute"


def test_credit_below_invoice_uses_normal_credit_path():
    assert expected_route(invoice_amount=1950, credit_amount=1900) == "normal_credit"


def test_equal_credit_is_not_dispute():
    assert expected_route(invoice_amount=1950, credit_amount=1950) == "normal_credit"


def test_score_result_accepts_correct_route(tmp_path):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"route": "dispute"}), encoding="utf-8")
    scored = score_result(invoice_amount=1950, credit_amount=2000, result_path=result_path)
    assert scored == {"pass": True, "expected": "dispute", "actual": "dispute"}


def test_score_result_rejects_wrong_route(tmp_path):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"route": "normal_credit"}), encoding="utf-8")
    scored = score_result(invoice_amount=1950, credit_amount=2000, result_path=result_path)
    assert scored == {"pass": False, "expected": "dispute", "actual": "normal_credit"}
