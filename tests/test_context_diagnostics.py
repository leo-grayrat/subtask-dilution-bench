import copy
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

FROZEN_POLICY_SOURCES = {
    "S01": ("finance_meridian_partners_158b9045", "SOP-FIN-AP-004.docx"),
    "S02": ("insurance_vanguard_shield_mutual_9b2f7a29", "SOP_VanguardShield.html"),
    "S04": ("medical_careig_specialty_pharmacy_f5947c33", "CareIG_SOP_v5.0.html"),
    "S07": (
        "insurance_vanguard_shield_mutual_82da8d17",
        "Vanguard_Shield_Core_Operations_SOP.html",
    ),
    "S08": ("finance_meridian_partners_a0895480", "Meridian Partners SOP.html"),
    "S09": ("finance_sunshine_set_d9d532c1", "Sunshine_Set_Automotive_SOP.pdf"),
    "S10": (
        "insurance_vanguard_shield_mutual_89007056",
        "Vanguard_Shield_Core_Operations_SOP.pdf",
    ),
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

    def test_default_registry_builds_three_tasks_for_each_frozen_mother_task(self):
        from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for source_task, policy_name in FROZEN_POLICY_SOURCES.values():
                policy = (
                    root
                    / "handbook/tasks"
                    / source_task
                    / "environment/initial_workspace"
                    / policy_name
                )
                policy.parent.mkdir(parents=True)
                policy.write_text(f"Policy source: {policy_name}\n", encoding="utf-8")

            tasks = build_diagnostic_tasks(root / "handbook", root / "generated")

            expected = {
                f"{case_id}:{condition}"
                for case_id in FROZEN_POLICY_SOURCES
                for condition in ("policy", "state_A", "state_B")
            }
            self.assertEqual(set(tasks), expected)
            self.assertEqual(len(tasks), 21)


def _good_case() -> dict:
    """返回一个满足全部四条不变量的合成登记表条目。"""
    return copy.deepcopy(SYNTHETIC_CASES["X01"])


def _build_synthetic_handbook(root: Path, sources) -> None:
    for source_task, policy_name in sources:
        policy = (
            root
            / "handbook/tasks"
            / source_task
            / "environment/initial_workspace"
            / policy_name
        )
        policy.parent.mkdir(parents=True)
        policy.write_text(f"Policy source: {policy_name}\n", encoding="utf-8")


class RegistryInvariantTests(unittest.TestCase):
    """校验 8e23014 引入的诊断登记表的四条不变量。

    1. 来源文件存在；
    2. A/B 目标动作互为相反；
    3. 动作值属于该母任务声明的允许集合（rule.action_options）；
    4. A/B 之间只翻转单一关键业务事实，不引入第二个阻断条件。
    """

    def _validate(self, cases, handbook_dir=None):
        from benchmarks.context_integration.diagnostics import (
            validate_diagnostic_registry,
        )

        return validate_diagnostic_registry(cases, handbook_dir=handbook_dir)

    def _issues_for(self, issues, case_id, invariant):
        return [
            issue
            for issue in issues
            if issue["case"] == case_id and issue["invariant"] == invariant
        ]

    # ---- 冻结登记表本身应通过全部不变量 ----

    def test_frozen_registry_passes_structure_invariants(self):
        from benchmarks.context_integration.diagnostics import load_diagnostic_cases

        issues = self._validate(load_diagnostic_cases())
        self.assertEqual(
            issues,
            [],
            f"冻结登记表违反不变量：{issues}",
        )

    def test_frozen_registry_source_files_exist_in_synthetic_handbook(self):
        from benchmarks.context_integration.diagnostics import load_diagnostic_cases

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, FROZEN_POLICY_SOURCES.values())
            issues = self._validate(
                load_diagnostic_cases(), handbook_dir=root / "handbook"
            )
            self.assertEqual(issues, [])

    # ---- 不变量 1：来源文件存在 ----

    def test_missing_source_file_is_reported(self):
        case = _good_case()
        case["policy_files"] = ["Policy.txt", "Missing_Addendum.txt"]

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, [("synthetic_source", "Policy.txt")])
            issues = self._validate({"X01": case}, handbook_dir=root / "handbook")

        self.assertEqual(len(self._issues_for(issues, "X01", "source_files")), 1)
        self.assertIn("Missing_Addendum.txt", issues[0]["message"])

    # ---- 不变量 2：A/B 动作相反 ----

    def test_identical_ab_actions_are_reported(self):
        case = _good_case()
        case["states"]["B"]["expected_action"] = "dispute"
        issues = self._validate({"X01": case})
        self.assertEqual(len(self._issues_for(issues, "X01", "action_flip")), 1)

    def test_ab_actions_must_cover_both_allowed_options(self):
        case = _good_case()
        case["rule"]["action_options"] = ["dispute", "normal_credit", "escalate"]
        issues = self._validate({"X01": case})
        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "action_flip")), 1
        )

    # ---- 不变量 3：动作属于允许集合 ----

    def test_state_action_outside_allowed_set_is_reported(self):
        case = _good_case()
        case["states"]["A"]["expected_action"] = "escalate"
        issues = self._validate({"X01": case})
        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "allowed_actions")), 1
        )

    def test_rule_action_outside_allowed_set_is_reported(self):
        case = _good_case()
        case["rule"]["when_false"] = "ask_manager"
        issues = self._validate({"X01": case})
        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "allowed_actions")), 1
        )

    # ---- 不变量 4：只翻转单一关键业务事实 ----

    def test_silent_change_of_non_supporting_fact_is_reported(self):
        case = _good_case()
        # 第二个事实 F1 在 B 中被顺便改掉，且未声明为支撑事实，
        # 可能引入第二个独立阻断条件。
        case["states"]["A"]["supporting_fact_ids"] = ["F2"]
        case["states"]["B"]["supporting_fact_ids"] = ["F2"]
        case["states"]["B"]["facts"][0]["text"] = "Invoice amount: 2,500."
        issues = self._validate({"X01": case})
        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "single_flipped_fact")), 1
        )

    def test_extra_fact_in_one_state_is_reported(self):
        case = _good_case()
        case["states"]["B"]["facts"].append(
            {"id": "F3", "text": "The customer account is suspended."}
        )
        issues = self._validate({"X01": case})
        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "single_flipped_fact")), 1
        )

    def test_no_flipped_fact_is_reported(self):
        case = _good_case()
        # A/B 事实完全相同，却声称动作应翻转，说明翻转事实缺失。
        case["states"]["B"]["facts"] = copy.deepcopy(case["states"]["A"]["facts"])
        issues = self._validate({"X01": case})
        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "single_flipped_fact")), 1
        )

    def test_declared_duplicate_representations_of_one_fact_pass(self):
        # 设计允许同一关键事实的多个重复表示同步修改（design.md 第 4 节），
        # 只要所有被修改的事实都被声明为支撑事实。
        case = _good_case()
        case["states"]["B"]["facts"][0]["text"] = (
            "Invoice amount: 1,950, confirmed again by the billing ledger."
        )
        issues = self._validate({"X01": case})
        self.assertEqual(
            self._issues_for(issues, "X01", "single_flipped_fact"), []
        )


if __name__ == "__main__":
    unittest.main()
