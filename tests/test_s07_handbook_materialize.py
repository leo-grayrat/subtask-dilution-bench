import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.context_integration.s07_beneficiary_survival.materialize import materialize


ISSUE_KEY = "CLM_LIFE-3"
EVIDENCE_FILE = "additional_document_drummond_01.pdf"


def _make_source(root: Path) -> None:
    workspace = root / "environment/initial_workspace"
    jira_dir = root / "environment/initial_external_services/jira"
    tests_dir = root / "tests"
    workspace.mkdir(parents=True)
    jira_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)

    (root / "instruction.md").write_text("Process all four life claims.\n", encoding="utf-8")
    (workspace / "Policy_LC-2018-06231_Declarations.pdf").write_bytes(b"policy")
    (workspace / "Death_Certificate_Drummond_Harold.pdf").write_bytes(b"insured-death")
    (workspace / EVIDENCE_FILE).write_bytes(b"beneficiary-death")
    (workspace / "keep.pdf").write_bytes(b"keep")

    jira = {
        "issues": {
            ISSUE_KEY: {
                "key": ISSUE_KEY,
                "fields": {
                    "status": {"name": "Open"},
                    "labels": ["life-claim"],
                    "attachment": [
                        {"id": "1", "filename": "Death_Certificate_Drummond_Harold.pdf"},
                        {"id": "2", "filename": "Policy_LC-2018-06231_Declarations.pdf"},
                        {"id": "3", "filename": EVIDENCE_FILE},
                    ],
                    "comment": {"comments": []},
                },
            },
            "CLM_LIFE-4": {"key": "CLM_LIFE-4", "fields": {"status": {"name": "Open"}}},
        }
    }
    (jira_dir / "jira_state.json").write_text(json.dumps(jira), encoding="utf-8")
    rubrics = [
        {"id": "other", "rubric_text": "CLM_LIFE-4 allocation", "verifier_code": "OTHER"},
        {"id": "old-target", "rubric_text": "CLM_LIFE-3 old allocation", "verifier_code": "OLD"},
    ]
    (tests_dir / "rubrics.json").write_text(json.dumps(rubrics), encoding="utf-8")


def _jira(root: Path) -> dict:
    path = root / "environment/initial_external_services/jira/jira_state.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _attachment_names(root: Path) -> list[str]:
    return [
        item["filename"]
        for item in _jira(root)["issues"][ISSUE_KEY]["fields"]["attachment"]
    ]


def _run_verifier(code: str, external: Path) -> dict:
    namespace = {}
    exec(code, namespace)
    return namespace["verify"](external.parent / "workspace", external)


def _result_state(root: Path, comment: str) -> Path:
    root.mkdir(parents=True)
    data = {
        "issues": {
            ISSUE_KEY: {
                "key": ISSUE_KEY,
                "fields": {
                    "status": {"name": "Route to AP for Payout"},
                    "labels": ["life-claim"],
                    "comment": {"comments": [{"body": comment}]},
                },
            }
        }
    }
    (root / "jira_state.json").write_text(json.dumps(data), encoding="utf-8")
    return root


class MaterializeS07Tests(unittest.TestCase):
    def test_local_a_keeps_evidence_and_uses_only_target_rubric(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="local", variant="A")

            self.assertTrue((out / f"environment/initial_workspace/{EVIDENCE_FILE}").exists())
            self.assertIn(EVIDENCE_FILE, _attachment_names(out))
            self.assertIn(ISSUE_KEY, (out / "instruction.md").read_text(encoding="utf-8"))
            rubrics = json.loads((out / "tests/rubrics.json").read_text(encoding="utf-8"))
            self.assertEqual([r["id"] for r in rubrics], ["S07-ALLOCATION"])

    def test_variant_b_removes_only_the_matching_evidence_file_and_attachment(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="B")

            self.assertFalse((out / f"environment/initial_workspace/{EVIDENCE_FILE}").exists())
            self.assertNotIn(EVIDENCE_FILE, _attachment_names(out))
            self.assertTrue((out / "environment/initial_workspace/keep.pdf").exists())
            self.assertEqual(
                set(_attachment_names(out)),
                {"Death_Certificate_Drummond_Harold.pdf", "Policy_LC-2018-06231_Declarations.pdf"},
            )
            self.assertEqual(_jira(src)["issues"]["CLM_LIFE-4"], _jira(out)["issues"]["CLM_LIFE-4"])

    def test_full_mode_keeps_unrelated_rubric_and_replaces_target_scoring(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, out = base / "src", base / "out"
            _make_source(src)

            materialize(src, out, mode="full", variant="A")

            rubrics = {r["id"]: r for r in json.loads((out / "tests/rubrics.json").read_text())}
            self.assertIn("other", rubrics)
            self.assertNotIn("old-target", rubrics)
            self.assertIn("S07-ALLOCATION", rubrics)

    def test_ambiguous_source_attachment_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            jira = _jira(src)
            jira["issues"][ISSUE_KEY]["fields"]["attachment"].append(
                {"id": "4", "filename": EVIDENCE_FILE}
            )
            path = src / "environment/initial_external_services/jira/jira_state.json"
            path.write_text(json.dumps(jira), encoding="utf-8")

            with self.assertRaises(RuntimeError):
                materialize(src, base / "out", mode="full", variant="B")

    def test_embedded_verifier_accepts_correct_a_and_b_allocations(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            comments = {
                "A": (
                    "Beneficiary Allocation — Policy LC-2018-06231 — Face Amount $600,000.00. "
                    "Linda Drummond excluded because she died before the insured. "
                    "Mark T. Drummond — Primary — 63.64% — $381,818.18. "
                    "Susan Drummond — Primary — 36.36% — $218,181.82. "
                    "George Drummond excluded as contingent. Analyst Taylor Morgan, 2026-04-10."
                ),
                "B": (
                    "Beneficiary Allocation — Policy LC-2018-06231 — Face Amount $600,000.00. "
                    "Linda Drummond — Primary — 45% — $270,000.00. "
                    "Mark T. Drummond — Primary — 35% — $210,000.00. "
                    "Susan Drummond — Primary — 20% — $120,000.00. "
                    "George Drummond excluded as contingent. Analyst Taylor Morgan, 2026-04-10."
                ),
            }
            for variant in ("A", "B"):
                task = base / f"task_{variant}"
                materialize(src, task, mode="local", variant=variant)
                rubric = json.loads((task / "tests/rubrics.json").read_text())[0]
                external = _result_state(base / f"external_{variant}", comments[variant])
                self.assertTrue(_run_verifier(rubric["verifier_code"], external)["pass"])

    def test_embedded_verifier_rejects_crossed_allocations(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "src"
            _make_source(src)
            wrong_comment = (
                "Beneficiary Allocation — Policy LC-2018-06231 — Face Amount $600,000.00. "
                "Linda Drummond — Primary — 45% — $270,000.00. "
                "Mark T. Drummond — Primary — 35% — $210,000.00. "
                "Susan Drummond — Primary — 20% — $120,000.00. "
                "George Drummond excluded as contingent. Analyst Taylor Morgan, 2026-04-10."
            )
            task = base / "task"
            materialize(src, task, mode="local", variant="A")
            rubric = json.loads((task / "tests/rubrics.json").read_text())[0]
            external = _result_state(base / "external", wrong_comment)
            self.assertFalse(_run_verifier(rubric["verifier_code"], external)["pass"])

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
