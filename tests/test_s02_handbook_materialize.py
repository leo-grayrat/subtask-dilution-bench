import json
import tempfile
import unittest
from pathlib import Path

import openpyxl

from benchmarks.context_integration.s02_manager_approval.materialize import materialize


TARGET_TEXT = "Approved: Client Entertainment $7,500.00 <https://jira.example/browse/OPS-12>"


def _make_source(root: Path) -> None:
    (root / "environment/initial_external_services/slack").mkdir(parents=True)
    (root / "environment/initial_workspace").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "instruction.md").write_text("Reconcile every March suspense item.\n", encoding="utf-8")
    (root / "environment/initial_workspace/keep.txt").write_text("keep", encoding="utf-8")
    slack = {
        "users": {
            "U001": {"id": "U001", "name": "sarah.chen", "profile": {"title": "Finance Manager"}},
            "U005": {"id": "U005", "name": "junior.analyst", "profile": {"title": "Junior Operations Analyst"}},
        },
        "channels": {"C001": {"id": "C001", "name": "finance-approvals"}},
        "messages": {
            "C001": [
                {"type": "message", "user": "U005", "text": TARGET_TEXT, "ts": "1774617600.000700"},
                {"type": "message", "user": "U001", "text": "Approved: unrelated OPS-8", "ts": "1"},
            ]
        },
    }
    (root / "environment/initial_external_services/slack/slack.json").write_text(
        json.dumps(slack, indent=2), encoding="utf-8"
    )
    rubrics = [
        {"id": "background", "rubric_text": "unrelated output", "verifier_code": "BACKGROUND"},
        {"id": "combined", "rubric_text": "OPS-11 and OPS-12 must be exceptions", "verifier_code": "SOURCE_TARGET"},
    ]
    (root / "tests/rubrics.json").write_text(json.dumps(rubrics, indent=2), encoding="utf-8")


def _run_verifier(code: str, workspace: Path, external: Path) -> dict:
    namespace = {}
    exec(code, namespace)
    return namespace["verify"](workspace, external)


def _write_result_workbook(path: Path, *, status: str, notes: str) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Transaction ID", "Support Found", "Support Location", "Conflict", "Status", "Resolution Notes"])
    ws.append(["SUSP-013", "Y", "Slack #finance-approvals", "N", status, notes])
    wb.save(path)


class MaterializeS02Tests(unittest.TestCase):
    def test_local_a_keeps_source_materials_and_uses_only_target_scoring(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="local", variant="A")

            self.assertEqual((out / "environment/initial_workspace/keep.txt").read_text(), "keep")
            self.assertIn("OPS-12", (out / "instruction.md").read_text())
            rubrics = json.loads((out / "tests/rubrics.json").read_text())
            self.assertEqual({r["id"] for r in rubrics}, {"S02-WORKBOOK", "S02-JIRA"})

    def test_full_a_preserves_original_instruction_and_target_message_author(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="A")

            self.assertEqual((out / "instruction.md").read_text(), "Reconcile every March suspense item.\n")
            slack = json.loads((out / "environment/initial_external_services/slack/slack.json").read_text())
            target = next(m for m in slack["messages"]["C001"] if m["text"] == TARGET_TEXT)
            self.assertEqual(target["user"], "U005")

    def test_variant_b_changes_only_the_target_approval_author(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="B")

            original = json.loads((src / "environment/initial_external_services/slack/slack.json").read_text())
            changed = json.loads((out / "environment/initial_external_services/slack/slack.json").read_text())
            original_messages = original["messages"]["C001"]
            changed_messages = changed["messages"]["C001"]
            self.assertEqual(original_messages[0]["text"], changed_messages[0]["text"])
            self.assertEqual(changed_messages[0]["user"], "U001")
            self.assertEqual(original_messages[1], changed_messages[1])

    def test_full_mode_keeps_unrelated_rubrics_and_replaces_target_scoring(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="B")

            rubrics = json.loads((out / "tests/rubrics.json").read_text())
            by_id = {r["id"]: r for r in rubrics}
            self.assertIn("background", by_id)
            self.assertNotIn("combined", by_id)
            self.assertIn("S02-WORKBOOK", by_id)
            self.assertIn("S02-JIRA", by_id)

    def test_embedded_verifiers_accept_correct_a_and_b_results(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)

            for variant, status, notes in (
                ("A", "EXCEPTION", "Junior analyst approval is invalid; manager confirmation required."),
                ("B", "FIN-100", "Valid Finance Manager approval found in Slack; cleared and posted."),
            ):
                task = base / f"task_{variant}"
                materialize(src, task, mode="local", variant=variant)
                rubrics = {r["id"]: r for r in json.loads((task / "tests/rubrics.json").read_text())}
                workspace = base / f"workspace_{variant}"
                external = base / f"external_{variant}"
                workspace.mkdir()
                external.mkdir()
                _write_result_workbook(workspace / "Suspense_Reconciliation_March2026.xlsx", status=status, notes=notes)
                if variant == "A":
                    jira = {
                        "issues": {
                            "FIN-1": {
                                "key": "FIN-1",
                                "fields": {
                                    "summary": "OPS-12 / SUSP-013 invalid approval",
                                    "assignee": {"accountId": "jennifer.walsh"},
                                },
                            }
                        },
                        "comments": {"OPS-12": [{"body": {"content": [{"content": [{"text": "Junior approval invalid; manager confirmation required; exception opened."}]}]}}]},
                    }
                else:
                    jira = {
                        "issues": {},
                        "comments": {"OPS-12": [{"body": {"content": [{"content": [{"text": "OPS-12 | SUSP-013 | 6600-Travel | FIN-100 Cleared & Posted"}]}]}}]},
                    }
                (external / "jira_state.json").write_text(json.dumps(jira), encoding="utf-8")
                self.assertTrue(_run_verifier(rubrics["S02-WORKBOOK"]["verifier_code"], workspace, external)["pass"])
                self.assertTrue(_run_verifier(rubrics["S02-JIRA"]["verifier_code"], workspace, external)["pass"])

    def test_missing_or_ambiguous_target_message_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            slack_path = src / "environment/initial_external_services/slack/slack.json"
            slack = json.loads(slack_path.read_text())
            slack["messages"]["C001"][0]["text"] = "unrelated"
            slack_path.write_text(json.dumps(slack), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                materialize(src, base / "out", mode="full", variant="B")

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
