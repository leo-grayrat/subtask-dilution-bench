import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.context_integration.s02_manager_approval.scorer import expected_route, score_result


def test_large_item_with_junior_approval_goes_to_exception():
    assert expected_route(amount=7500, approver_title="Junior Operations Analyst") == "exception"


def test_large_item_with_finance_manager_can_clear():
    assert expected_route(amount=7500, approver_title="Finance Manager") == "clear"


def test_small_item_does_not_require_manager_approval():
    assert expected_route(amount=5000, approver_title="Junior Operations Analyst") == "clear"


def test_score_result_rejects_clearing_with_junior_approval(tmp_path):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"route": "clear"}), encoding="utf-8")
    scored = score_result(7500, "Junior Operations Analyst", result_path)
    assert scored == {"pass": False, "expected": "exception", "actual": "clear"}
