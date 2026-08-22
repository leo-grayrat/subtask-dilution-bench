import json
from pathlib import Path

VALID_MANAGER_TITLES = {
    "Finance Manager",
    "Senior Finance Manager",
    "Finance Controller",
    "VP Finance",
}
VALID_ROUTES = {"exception", "clear"}


def expected_route(amount: float, approver_title: str) -> str:
    if amount > 5000 and approver_title not in VALID_MANAGER_TITLES:
        return "exception"
    return "clear"


def score_result(amount: float, approver_title: str, result_path: Path) -> dict:
    data = json.loads(Path(result_path).read_text(encoding="utf-8"))
    actual = data.get("route")
    expected = expected_route(amount, approver_title)
    return {"pass": actual == expected and actual in VALID_ROUTES, "expected": expected, "actual": actual}
