import json
from pathlib import Path

VALID_ROUTES = {"dispute", "normal_credit"}


def expected_route(invoice_amount: float, credit_amount: float) -> str:
    return "dispute" if credit_amount > invoice_amount else "normal_credit"


def score_result(invoice_amount: float, credit_amount: float, result_path: Path) -> dict:
    data = json.loads(Path(result_path).read_text(encoding="utf-8"))
    actual = data.get("route")
    if actual not in VALID_ROUTES:
        return {"pass": False, "expected": expected_route(invoice_amount, credit_amount), "actual": actual}
    expected = expected_route(invoice_amount, credit_amount)
    return {"pass": actual == expected, "expected": expected, "actual": actual}
