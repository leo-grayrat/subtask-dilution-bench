from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path


ISSUE_KEY = "OPS_HR_TE-4"
EMPLOYEE_EMAIL = "derek.washington@vanguardshield.com"
SHOPIFY_FILE = "shopify_data.json"
PRODUCT_ID = "gid://shopify/Product/5002"
ORDER_ID = "gid://shopify/Order/c2004"
LINE_ID = "gid://shopify/OrderLine/3004"
LOCAL_INSTRUCTION = (
    "Audit only pending Sales expense report OPS_HR_TE-4. Read the report, the relevant calendar "
    "and internal store records, and the Vanguard Shield Core Operations SOP, then complete every "
    "required action for this report.\n"
)


def _decision_verifier(variant: str) -> str:
    return f'''from pathlib import Path
import json

VARIANT = {variant!r}

def _text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        own = str(node.get("text", "")) if node.get("type") == "text" else ""
        return own + " ".join(_text(child) for child in node.get("content", []))
    if isinstance(node, list):
        return " ".join(_text(item) for item in node)
    return ""

def verify(workspace_path, external_services_path=None):
    if external_services_path is None:
        return {{"pass": False, "score": 0.0, "feedback": "external services path missing"}}
    path = Path(external_services_path) / "jira_state.json"
    if not path.exists():
        return {{"pass": False, "score": 0.0, "feedback": "jira_state.json not found"}}
    data = json.loads(path.read_text(encoding="utf-8"))
    issues = data.get("issues", {{}})
    issue = issues.get("OPS_HR_TE-4") if isinstance(issues, dict) else None
    if not isinstance(issue, dict):
        return {{"pass": False, "score": 0.0, "feedback": "OPS_HR_TE-4 not found"}}
    parts = []
    for comment in data.get("comments", {{}}).get("OPS_HR_TE-4", []):
        parts.append(_text(comment.get("body", comment)) if isinstance(comment, dict) else _text(comment))
    fields = issue.get("fields", {{}})
    comment_field = fields.get("comment", {{}}) if isinstance(fields, dict) else {{}}
    if isinstance(comment_field, dict):
        for comment in comment_field.get("comments", []):
            parts.append(_text(comment.get("body", comment)) if isinstance(comment, dict) else _text(comment))
    comments = " ".join(parts).lower()
    failures = []
    if VARIANT == "A":
        if "unauthorized vendor" not in comments:
            failures.append("unauthorized-vendor decision missing")
        if "personal reimbursement" not in comments or "line item" not in comments or "1" not in comments:
            failures.append("line item 1 personal reimbursement instruction missing")
        if "all lines supported" in comments:
            failures.append("unsupported report was incorrectly marked fully supported")
    else:
        if "t&e review complete" not in comments or "all lines supported" not in comments:
            failures.append("fully supported review comment missing")
        if "unauthorized vendor" in comments or "personal reimbursement" in comments or "missing business justification" in comments:
            failures.append("supported report contains an incorrect rejection reason")
    return {{
        "pass": not failures,
        "score": 1.0 if not failures else 0.0,
        "feedback": "ok" if not failures else "; ".join(failures),
    }}
'''


def _target_rubric(variant: str) -> dict:
    if variant == "A":
        expectation = (
            "No matching completed internal-store order exists for Derek Washington's $420 polo "
            "purchase, so comment that line item 1 is an unauthorized vendor purchase and requires personal reimbursement."
        )
    else:
        expectation = (
            "A paid and fulfilled $420 internal-store order matches Derek Washington's polo purchase; "
            "with the mileage line supported, comment that the review is complete and all lines are supported."
        )
    return {
        "id": "S10-DECISION",
        "sort_order": 100,
        "rubric_text": f"For {ISSUE_KEY}, {expectation}",
        "verifier_code": _decision_verifier(variant),
        "criterion_type": "expected_output",
    }


def _shopify_path(task: Path) -> Path:
    return task / "environment/initial_external_services/shopify" / SHOPIFY_FILE


def _validated_template(data: dict) -> dict:
    orders = data.get("orders")
    if not isinstance(orders, dict):
        raise RuntimeError("Shopify order collection missing")
    derek_orders = [
        order for order in orders.values()
        if str(order.get("buyerIdentity", {}).get("email", "")).lower() == EMPLOYEE_EMAIL
    ]
    if derek_orders:
        raise RuntimeError("source unexpectedly already contains a Derek Washington order")
    templates = []
    for order in orders.values():
        items = order.get("lineItems", [])
        if len(items) == 1 and items[0].get("productId") == PRODUCT_ID:
            templates.append(order)
    if len(templates) != 1:
        raise RuntimeError(f"expected one single-line polo order template, found {len(templates)}")
    counters = data.get("counters", {})
    if counters.get("order_id") != 2003 or counters.get("line_id") != 3003:
        raise RuntimeError("unexpected Shopify counters for source task")
    if ORDER_ID in orders:
        raise RuntimeError(f"target order id already exists: {ORDER_ID}")
    return templates[0]


def _set_money(container: dict, key: str, amount: str) -> None:
    value = container.get(key)
    if isinstance(value, dict):
        value["amount"] = amount


def _build_order(template: dict) -> dict:
    order = copy.deepcopy(template)
    order["id"] = ORDER_ID
    order["orderNumber"] = "#VS-2004"
    order["name"] = "#VS-2004"
    order["statusUrl"] = "https://internal-store.vanguardshield.com/orders/c2004"
    order["financialStatus"] = "PAID"
    order["fulfillmentStatus"] = "FULFILLED"
    order["createdAt"] = "2026-04-01T09:00:00.000000Z"
    order["updatedAt"] = "2026-04-01T09:05:00.000000Z"
    order["buyerIdentity"] = {"email": EMPLOYEE_EMAIL}
    order["totalQuantity"] = 15

    lines = order.get("lines", [])
    items = order.get("lineItems", [])
    if len(lines) != 1 or len(items) != 1:
        raise RuntimeError("polo order template must contain one line in both representations")
    lines[0]["id"] = LINE_ID
    lines[0]["quantity"] = 15
    line_cost = lines[0].get("cost", {})
    _set_money(line_cost, "subtotalAmount", "420.00")
    _set_money(line_cost, "totalAmount", "420.00")
    items[0]["id"] = LINE_ID
    items[0]["quantity"] = 15
    _set_money(items[0], "totalPrice", "420.00")
    for key in ("subtotalAmount", "totalAmount", "checkoutChargeAmount"):
        _set_money(order.get("cost", {}), key, "420.00")
    _set_money(order, "subtotalPrice", "420.00")
    _set_money(order, "totalPrice", "420.00")
    return order


def _is_target_decision_rubric(rubric: dict) -> bool:
    text = str(rubric.get("rubric_text", "")).lower()
    if ISSUE_KEY.lower() not in text:
        return False
    return "unauthorized vendor" in text or "all lines supported" in text


def materialize(source_task_dir: str | Path, output_dir: str | Path, *, mode: str, variant: str) -> None:
    if mode not in {"local", "full"}:
        raise ValueError("mode must be 'local' or 'full'")
    if variant not in {"A", "B"}:
        raise ValueError("variant must be 'A' or 'B'")
    source = Path(source_task_dir)
    output = Path(output_dir)
    if not source.is_dir():
        raise FileNotFoundError(source)
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output)

    shopify_path = _shopify_path(output)
    shopify = json.loads(shopify_path.read_text(encoding="utf-8"))
    template = _validated_template(shopify)
    if variant == "B":
        shopify["orders"][ORDER_ID] = _build_order(template)
        shopify["counters"]["order_id"] = 2004
        shopify["counters"]["line_id"] = 3004
        shopify_path.write_text(json.dumps(shopify, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if mode == "local":
        (output / "instruction.md").write_text(LOCAL_INSTRUCTION, encoding="utf-8")

    rubrics_path = output / "tests/rubrics.json"
    rubrics = json.loads(rubrics_path.read_text(encoding="utf-8"))
    target = _target_rubric(variant)
    if mode == "local":
        rubrics = [target]
    else:
        rubrics = [rubric for rubric in rubrics if not _is_target_decision_rubric(rubric)]
        rubrics.append(target)
    rubrics_path.write_text(json.dumps(rubrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build S10 HANDBOOK local/full A/B task variants")
    parser.add_argument("source_task_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--mode", choices=["local", "full"], required=True)
    parser.add_argument("--variant", choices=["A", "B"], required=True)
    args = parser.parse_args()
    materialize(args.source_task_dir, args.output_dir, mode=args.mode, variant=args.variant)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
