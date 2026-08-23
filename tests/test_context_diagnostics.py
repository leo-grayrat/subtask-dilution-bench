import json
import tempfile
import unittest
from pathlib import Path


SYNTHETIC_CASES = {
    "X01": {
        "source_task": "synthetic_source",
        "subject": "whether a credit should enter dispute handling",
        "policy_files": ["Policy.txt"],
        "rule": {
            "text": "Use dispute handling only when the credit is greater than the invoice.",
            "condition_options": [
                "credit_amount_gt_invoice_amount",
                "credit_amount_lt_invoice_amount",
            ],
            "condition": "credit_amount_gt_invoice_amount",
            "action_options": ["dispute", "normal_credit"],
            "when_true": "dispute",
            "when_false": "normal_credit",
        },
        "states": {
            "A": {
                "facts": [
                    {"id": "F1", "text": "Invoice amount: 1,950."},
                    {"id": "F2", "text": "Credit amount: 2,000."},
                ],
                "expected_action": "dispute",
                "supporting_fact_ids": ["F1", "F2"],
            },
            "B": {
                "facts": [
                    {"id": "F1", "text": "Invoice amount: 1,950."},
                    {"id": "F2", "text": "Credit amount: 1,900."},
                ],
                "expected_action": "normal_credit",
                "supporting_fact_ids": ["F1", "F2"],
            },
        },
    }
}


class ContextDiagnosticTaskTests(unittest.TestCase):
    def test_builder_creates_one_policy_task_and_two_state_tasks(self):
        try:
            from benchmarks.context_integration.diagnostics import build_diagnostic_tasks
        except ModuleNotFoundError as exc:
            self.fail(f"diagnostic task builder is missing: {exc}")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            policy = (
                root
                / "handbook/tasks/synthetic_source/environment/initial_workspace/Policy.txt"
            )
            policy.parent.mkdir(parents=True)
            policy.write_text("Complete policy handbook.\n", encoding="utf-8")

            tasks = build_diagnostic_tasks(
                root / "handbook",
                root / "generated",
                cases=SYNTHETIC_CASES,
            )

            self.assertEqual(
                set(tasks),
                {"X01:policy", "X01:state_A", "X01:state_B"},
            )
            policy_task = tasks["X01:policy"]
            self.assertEqual(
                (policy_task / "reference/Policy.txt").read_text(encoding="utf-8"),
                "Complete policy handbook.\n",
            )
            self.assertTrue((policy_task / "SYSTEM.md").is_file())
            self.assertTrue((policy_task / "WORK_ORDER.md").is_file())
            self.assertFalse((policy_task / "answer.json").exists())

            for condition in ("state_A", "state_B"):
                task = tasks[f"X01:{condition}"]
                self.assertTrue((task / "SYSTEM.md").is_file())
                self.assertTrue((task / "WORK_ORDER.md").is_file())
                self.assertTrue((task / "POLICY.md").is_file())
                self.assertTrue((task / "STATE.md").is_file())
                self.assertFalse((task / "answer.json").exists())

    def test_policy_answer_requires_every_frozen_rule_field(self):
        from benchmarks.context_integration import diagnostics

        self.assertTrue(
            hasattr(diagnostics, "score_diagnostic_answer"),
            "diagnostic scorer is missing",
        )

        with tempfile.TemporaryDirectory() as td:
            answer = Path(td) / "answer.json"
            answer.write_text(
                json.dumps(
                    {
                        "condition": "credit_amount_gt_invoice_amount",
                        "when_true": "dispute",
                        "when_false": "dispute",
                        "source_file": "Policy.txt",
                        "rule_summary": "Larger credits use the dispute route.",
                    }
                ),
                encoding="utf-8",
            )

            result = diagnostics.score_diagnostic_answer(
                answer,
                case_id="X01",
                condition="policy",
                cases=SYNTHETIC_CASES,
            )

            self.assertFalse(result["pass"])
            self.assertEqual(result["score"], 0.75)
            self.assertEqual(
                result["checks"],
                {
                    "condition": True,
                    "when_true": True,
                    "when_false": False,
                    "source_file": True,
                },
            )

    def test_state_answers_follow_the_mirrored_fact(self):
        from benchmarks.context_integration.diagnostics import score_diagnostic_answer

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            examples = {
                "state_A": ("dispute", ["F1", "F2"]),
                "state_B": ("normal_credit", ["F2", "F1"]),
            }
            for condition, (action, fact_ids) in examples.items():
                with self.subTest(condition=condition):
                    answer = root / f"{condition}.json"
                    answer.write_text(
                        json.dumps(
                            {
                                "action": action,
                                "supporting_fact_ids": fact_ids,
                                "reasoning": "The two amounts determine the route.",
                            }
                        ),
                        encoding="utf-8",
                    )

                    result = score_diagnostic_answer(
                        answer,
                        case_id="X01",
                        condition=condition,
                        cases=SYNTHETIC_CASES,
                    )

                    self.assertTrue(result["pass"])
                    self.assertEqual(result["score"], 1.0)
                    self.assertEqual(
                        result["checks"],
                        {"action": True, "supporting_fact_ids": True, "reasoning": True},
                    )


if __name__ == "__main__":
    unittest.main()
