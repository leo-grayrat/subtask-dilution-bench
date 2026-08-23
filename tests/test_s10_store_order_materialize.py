import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.context_integration.s10_store_order.materialize import materialize


ISSUE_KEY = "OPS_HR_TE-4"
EMPLOYEE_EMAIL = "derek.washington@vanguardshield.com"


def _template_order() -> dict:
    return {
        "id": "gid://shopify/Order/c2003",
        "orderNumber": "#VS-2003",
        "name": "#VS-2003",
        "statusUrl": "https://internal-store.vanguardshield.com/orders/c2003",
        "financialStatus": "PAID",
        "fulfillmentStatus": "FULFILLED",
        "createdAt": "2026-03-10T09:00:00.000000Z",
        "updatedAt": "2026-03-10T09:05:00.000000Z",
        "buyerIdentity": {"email": "aisha.robinson@vanguardshield.com"},
        "lines": [{
            "id": "gid://shopify/OrderLine/3003",
            "quantity": 5,
            "merchandise": {
                "id": "gid://shopify/ProductVariant/5002-l",
                "title": "L",
                "product": {"id": "gid://shopify/Product/5002", "title": "Vanguard Shield Custom Polo Shirt"},
                "price": {"amount": "28.00", "currencyCode": "USD"},
            },
            "cost": {
                "subtotalAmount": {"amount": "140.00", "currencyCode": "USD"},
                "totalAmount": {"amount": "140.00", "currencyCode": "USD"},
            },
        }],
        "lineItems": [{
            "id": "gid://shopify/OrderLine/3003",
            "title": "Vanguard Shield Custom Polo Shirt",
            "quantity": 5,
            "price": {"amount": "28.00", "currencyCode": "USD"},
            "totalPrice": {"amount": "140.00", "currencyCode": "USD"},
            "variantId": "gid://shopify/ProductVariant/5002-l",
            "productId": "gid://shopify/Product/5002",
        }],
        "cost": {
            "subtotalAmount": {"amount": "140.00", "currencyCode": "USD"},
            "totalAmount": {"amount": "140.00", "currencyCode": "USD"},
            "checkoutChargeAmount": {"amount": "140.00", "currencyCode": "USD"},
        },
        "subtotalPrice": {"amount": "140.00", "currencyCode": "USD"},
        "totalPrice": {"amount": "140.00", "currencyCode": "USD"},
        "totalQuantity": 5,
    }


def _make_source(root: Path) -> None:
    shopify_dir = root / "environment/initial_external_services/shopify"
    tests = root / "tests"
    shopify_dir.mkdir(parents=True)
    tests.mkdir(parents=True)
    (root / "environment/initial_workspace").mkdir(parents=True)
    (root / "environment/initial_workspace/keep.txt").write_text("keep", encoding="utf-8")
    (root / "instruction.md").write_text("Audit all pending Sales expense reports.\n", encoding="utf-8")
    shopify = {
        "products": {"gid://shopify/Product/5002": {"title": "Vanguard Shield Custom Polo Shirt"}},
        "orders": {"gid://shopify/Order/c2003": _template_order()},
        "policies": [],
        "counters": {"order_id": 2003, "line_id": 3003},
    }
    (shopify_dir / "shopify_data.json").write_text(json.dumps(shopify), encoding="utf-8")
    rubrics = [
        {"id": "reject", "rubric_text": "OPS_HR_TE-4 Unauthorized vendor. Please submit personal reimbursement for line item: 1.", "verifier_code": "OLD"},
        {"id": "forbid-approve", "rubric_text": "OPS_HR_TE-4 must NOT contain T&E review complete—all lines supported", "verifier_code": "OLD2"},
        {"id": "manager", "rubric_text": "Email reporting manager lookup for OPS_HR_TE-4", "verifier_code": "KEEP"},
        {"id": "other", "rubric_text": "OPS_HR_TE-3 missing justification", "verifier_code": "OTHER"},
    ]
    (tests / "rubrics.json").write_text(json.dumps(rubrics), encoding="utf-8")


def _shopify(root: Path) -> dict:
    path = root / "environment/initial_external_services/shopify/shopify_data.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run_verifier(code: str, external: Path) -> dict:
    namespace = {}
    exec(code, namespace)
    return namespace["verify"](external.parent / "workspace", external)


def _result(root: Path, comment: str) -> Path:
    root.mkdir(parents=True)
    data = {
        "issues": {ISSUE_KEY: {"key": ISSUE_KEY, "fields": {"comment": {"comments": []}}}},
        "comments": {ISSUE_KEY: [{"body": comment}]},
    }
    (root / "jira_state.json").write_text(json.dumps(data), encoding="utf-8")
    return root


class MaterializeS10Tests(unittest.TestCase):
    def test_local_a_has_no_derek_order_and_only_target_rubric(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="local", variant="A")

            orders = _shopify(out)["orders"].values()
            self.assertFalse(any(o.get("buyerIdentity", {}).get("email") == EMPLOYEE_EMAIL for o in orders))
            self.assertIn(ISSUE_KEY, (out / "instruction.md").read_text(encoding="utf-8"))
            rubrics = json.loads((out / "tests/rubrics.json").read_text())
            self.assertEqual([r["id"] for r in rubrics], ["S10-DECISION"])

    def test_variant_b_adds_one_paid_fulfilled_matching_order(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="B")

            data = _shopify(out)
            matches = [o for o in data["orders"].values() if o.get("buyerIdentity", {}).get("email") == EMPLOYEE_EMAIL]
            self.assertEqual(len(matches), 1)
            order = matches[0]
            self.assertEqual(order["financialStatus"], "PAID")
            self.assertEqual(order["fulfillmentStatus"], "FULFILLED")
            self.assertEqual(order["totalPrice"]["amount"], "420.00")
            self.assertEqual(order["totalQuantity"], 15)
            self.assertEqual(order["lineItems"][0]["title"], "Vanguard Shield Custom Polo Shirt")
            self.assertEqual(data["counters"], {"order_id": 2004, "line_id": 3004})
            self.assertEqual(_shopify(src)["orders"]["gid://shopify/Order/c2003"], data["orders"]["gid://shopify/Order/c2003"])

    def test_full_mode_keeps_unrelated_and_manager_rubrics_but_replaces_decision_rubrics(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="B")

            rubrics = {r["id"]: r for r in json.loads((out / "tests/rubrics.json").read_text())}
            self.assertIn("manager", rubrics)
            self.assertIn("other", rubrics)
            self.assertNotIn("reject", rubrics)
            self.assertNotIn("forbid-approve", rubrics)
            self.assertIn("S10-DECISION", rubrics)

    def test_existing_derek_order_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            path = src / "environment/initial_external_services/shopify/shopify_data.json"
            data = _shopify(src)
            data["orders"]["gid://shopify/Order/c2003"]["buyerIdentity"]["email"] = EMPLOYEE_EMAIL
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                materialize(src, base / "out", mode="full", variant="B")

    def test_embedded_verifier_accepts_correct_a_and_b_results(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            comments = {
                "A": "Unauthorized vendor. Please submit personal reimbursement for line item: 1.",
                "B": "T&E review complete—all lines supported. OPS_HR_TE-4.",
            }
            for variant in ("A", "B"):
                task = base / f"task_{variant}"
                materialize(src, task, mode="local", variant=variant)
                rubric = json.loads((task / "tests/rubrics.json").read_text())[0]
                self.assertTrue(_run_verifier(rubric["verifier_code"], _result(base / f"result_{variant}", comments[variant]))["pass"])

    def test_embedded_verifier_rejects_crossed_result(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            task = base / "task"
            materialize(src, task, mode="local", variant="A")
            rubric = json.loads((task / "tests/rubrics.json").read_text())[0]
            wrong = _result(base / "result", "T&E review complete—all lines supported. OPS_HR_TE-4.")
            self.assertFalse(_run_verifier(rubric["verifier_code"], wrong)["pass"])

    def test_invalid_mode_or_variant_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            _make_source(src)
            with self.assertRaises(ValueError):
                materialize(src, Path(td) / "x", mode="tiny", variant="A")
            with self.assertRaises(ValueError):
                materialize(src, Path(td) / "y", mode="full", variant="C")


if __name__ == "__main__":
    unittest.main()
