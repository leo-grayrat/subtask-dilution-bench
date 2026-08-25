import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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


class RecallIntegrityTests(unittest.TestCase):
    """校验 Recall 任务包携带的规则文件与原始来源文件逐字节一致。

    Recall 包（``{case_id}_policy``）把登记表 ``policy_files`` 列出的来源规则文件
    复制进 ``reference/``。这里用 SHA-256 证明包内文件完整、未被改写、未被截断；
    来源文件缺失时必须给出清晰错误而不是静默通过。
    """

    def _verify(self, output_root, handbook_dir, cases=None):
        from benchmarks.context_integration.diagnostics import (
            verify_recall_package_integrity,
        )

        return verify_recall_package_integrity(output_root, handbook_dir, cases=cases)

    def _issues_for(self, issues, case_id, invariant):
        return [
            issue
            for issue in issues
            if issue["case"] == case_id and issue["invariant"] == invariant
        ]

    def _sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def test_recall_packages_carry_unmodified_source_files(self):
        from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, FROZEN_POLICY_SOURCES.values())
            tasks = build_diagnostic_tasks(root / "handbook", root / "generated")

            for case_id, (source_task, policy_name) in FROZEN_POLICY_SOURCES.items():
                with self.subTest(case_id=case_id):
                    source = (
                        root
                        / "handbook/tasks"
                        / source_task
                        / "environment/initial_workspace"
                        / policy_name
                    )
                    copied = tasks[f"{case_id}:policy"] / "reference" / policy_name
                    self.assertEqual(
                        self._sha256(copied.read_bytes()),
                        self._sha256(source.read_bytes()),
                        "Recall 包内规则文件与来源文件字节不一致",
                    )

            issues = self._verify(root / "generated", root / "handbook")
            self.assertEqual(issues, [], f"Recall 包完整性校验未通过：{issues}")

    def test_rewritten_or_truncated_package_file_is_detected(self):
        from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

        corruptions = {
            "rewritten": lambda data: data + b"\ntampered rewrite\n",
            "truncated": lambda data: data[: len(data) // 2],
        }
        for kind, corrupt in corruptions.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    _build_synthetic_handbook(
                        root, [("synthetic_source", "Policy.txt")]
                    )
                    build_diagnostic_tasks(
                        root / "handbook",
                        root / "generated",
                        cases=SYNTHETIC_CASES,
                    )
                    source = (
                        root
                        / "handbook/tasks/synthetic_source"
                        / "environment/initial_workspace/Policy.txt"
                    )
                    copied = root / "generated/X01_policy/reference/Policy.txt"
                    copied.write_bytes(corrupt(source.read_bytes()))

                    issues = self._verify(
                        root / "generated", root / "handbook", cases=SYNTHETIC_CASES
                    )

                    sha_issues = self._issues_for(issues, "X01", "recall_sha256")
                    self.assertEqual(
                        len(sha_issues),
                        1,
                        f"{kind} 场景未被哈希校验抓到：{issues}",
                    )
                    self.assertIn(self._sha256(source.read_bytes()), sha_issues[0]["message"])

    def test_missing_package_file_is_reported(self):
        from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, [("synthetic_source", "Policy.txt")])
            build_diagnostic_tasks(
                root / "handbook", root / "generated", cases=SYNTHETIC_CASES
            )
            (root / "generated/X01_policy/reference/Policy.txt").unlink()

            issues = self._verify(
                root / "generated", root / "handbook", cases=SYNTHETIC_CASES
            )

        self.assertEqual(len(self._issues_for(issues, "X01", "recall_package_file")), 1)

    def test_missing_source_file_is_reported_not_silently_passed(self):
        from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, [("synthetic_source", "Policy.txt")])
            build_diagnostic_tasks(
                root / "handbook", root / "generated", cases=SYNTHETIC_CASES
            )
            # 生成后来源文件不可用（例如指向了错误的 HANDBOOK 工作区），
            # 校验必须显式报告而不是静默通过。
            (
                root
                / "handbook/tasks/synthetic_source/environment/initial_workspace/Policy.txt"
            ).unlink()

            issues = self._verify(
                root / "generated", root / "handbook", cases=SYNTHETIC_CASES
            )

        self.assertEqual(len(self._issues_for(issues, "X01", "recall_source_file")), 1)

    def test_builder_rejects_corrupted_copy(self):
        from benchmarks.context_integration import diagnostics

        def corrupting_copy(src, dst, **kwargs):
            Path(dst).write_bytes(Path(src).read_bytes() + b"\nsilent rewrite\n")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, [("synthetic_source", "Policy.txt")])
            with mock.patch.object(
                diagnostics.shutil, "copy2", side_effect=corrupting_copy
            ):
                with self.assertRaises(RuntimeError):
                    diagnostics.build_diagnostic_tasks(
                        root / "handbook",
                        root / "generated",
                        cases=SYNTHETIC_CASES,
                    )


class ApplicabilityPairConsistencyTests(unittest.TestCase):
    """校验 Applicability A/B 任务包除状态事实外完全一致。

    Applicability 包（``{case_id}_state_A`` / ``{case_id}_state_B``）是同一母任务的
    两个镜像状态（design.md 第 4 节：只允许翻转一个关键业务事实）。除 STATE.md 中
    被翻转事实的文本行外，规则文本（POLICY.md）、工单措辞与动作选项顺序
    （WORK_ORDER.md）、系统提示（SYSTEM.md）、事实呈现顺序和任何其他文件都不得
    有差异，否则模型可能靠无关线索而不是规则推理作答。
    """

    def _verify(self, output_root, cases=None):
        from benchmarks.context_integration.diagnostics import (
            verify_applicability_pair_consistency,
        )

        return verify_applicability_pair_consistency(output_root, cases=cases)

    def _issues_for(self, issues, case_id, invariant):
        return [
            issue
            for issue in issues
            if issue["case"] == case_id and issue["invariant"] == invariant
        ]

    def _build_synthetic_packages(self, root: Path) -> Path:
        from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

        _build_synthetic_handbook(root, [("synthetic_source", "Policy.txt")])
        build_diagnostic_tasks(
            root / "handbook", root / "generated", cases=SYNTHETIC_CASES
        )
        return root / "generated"

    def _rewrite_file(self, path: Path, transform) -> None:
        path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")

    # ---- 冻结母任务与合成案例：差异只出现在状态事实时必须通过 ----

    def test_frozen_applicability_pairs_are_identical_outside_state_facts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, FROZEN_POLICY_SOURCES.values())
            from benchmarks.context_integration.diagnostics import (
                build_diagnostic_tasks,
            )

            build_diagnostic_tasks(root / "handbook", root / "generated")

            issues = self._verify(root / "generated")
            self.assertEqual(
                issues, [], f"冻结母任务的 Applicability A/B 包不一致：{issues}"
            )

    def test_differences_limited_to_flipped_fact_pass_without_false_positives(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generated = self._build_synthetic_packages(root)

            # 未触碰时通过。
            self.assertEqual(
                self._verify(generated, cases=SYNTHETIC_CASES), []
            )

            # 把 B 包被翻转事实 F2 改成另一个仍然不同的值，差异仍只在
            # 状态事实载体内，校验不得误报。
            self._rewrite_file(
                generated / "X01_state_B/STATE.md",
                lambda text: text.replace(
                    "- [F2] Credit amount: 1,900.",
                    "- [F2] Credit amount: 1,800.",
                ),
            )
            issues = self._verify(generated, cases=SYNTHETIC_CASES)
            self.assertEqual(
                issues, [], f"仅状态事实内的差异被误报为违规：{issues}"
            )

    # ---- 非状态事实字段被改动必须被抓到 ----

    def test_changed_rule_text_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generated = self._build_synthetic_packages(root)
            self._rewrite_file(
                generated / "X01_state_B/POLICY.md",
                lambda text: text + "Always prefer the dispute route.\n",
            )

            issues = self._verify(generated, cases=SYNTHETIC_CASES)

        content_issues = self._issues_for(issues, "X01", "applicability_pair_content")
        self.assertEqual(len(content_issues), 1)
        self.assertIn("POLICY.md", content_issues[0]["message"])

    def test_changed_wording_or_action_option_order_is_reported(self):
        tamperings = {
            "wording": lambda text: text.replace(
                "decide the correct action", "quickly guess the action"
            ),
            "action_option_order": lambda text: text.replace(
                "`dispute`, `normal_credit`", "`normal_credit`, `dispute`"
            ),
        }
        for kind, tamper in tamperings.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    generated = self._build_synthetic_packages(root)
                    self._rewrite_file(
                        generated / "X01_state_B/WORK_ORDER.md", tamper
                    )

                    issues = self._verify(generated, cases=SYNTHETIC_CASES)

                self.assertGreaterEqual(
                    len(self._issues_for(issues, "X01", "applicability_pair_content")),
                    1,
                    f"{kind} 场景未被抓到：{issues}",
                )

    def test_changed_system_prompt_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generated = self._build_synthetic_packages(root)
            self._rewrite_file(
                generated / "X01_state_A/SYSTEM.md",
                lambda text: text + "Prefer shorter answers.\n",
            )

            issues = self._verify(generated, cases=SYNTHETIC_CASES)

        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "applicability_pair_content")), 1
        )

    def test_extra_or_missing_package_file_is_reported(self):
        scenarios = {
            "extra_file_in_B": lambda generated: (
                generated / "X01_state_B/HINT.md"
            ).write_text("The answer is normal_credit.\n", encoding="utf-8"),
            "missing_file_in_A": lambda generated: (
                generated / "X01_state_A/POLICY.md"
            ).unlink(),
            "missing_package_directory": lambda generated: shutil.rmtree(
                generated / "X01_state_B"
            ),
        }
        for kind, tamper in scenarios.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    generated = self._build_synthetic_packages(root)
                    tamper(generated)

                    issues = self._verify(generated, cases=SYNTHETIC_CASES)

                self.assertGreaterEqual(
                    len(self._issues_for(issues, "X01", "applicability_pair_files")),
                    1,
                    f"{kind} 场景未被抓到：{issues}",
                )

    def test_state_changes_outside_flipped_fact_are_reported(self):
        tamperings = {
            "header_rewording": lambda text: text.replace(
                "# Current state", "# Current situation"
            ),
            "fact_order_swapped": lambda text: (
                "# Current state\n\n"
                "- [F2] Credit amount: 1,900.\n"
                "- [F1] Invoice amount: 1,950.\n"
            ),
            "extra_fact_line": lambda text: text + "- [F3] The account is suspended.\n",
            "non_flipped_fact_changed": lambda text: text.replace(
                "- [F1] Invoice amount: 1,950.",
                "- [F1] Invoice amount: 2,500.",
            ),
        }
        for kind, tamper in tamperings.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    generated = self._build_synthetic_packages(root)
                    self._rewrite_file(
                        generated / "X01_state_B/STATE.md", tamper
                    )

                    issues = self._verify(generated, cases=SYNTHETIC_CASES)

                self.assertGreaterEqual(
                    len(self._issues_for(issues, "X01", "applicability_pair_state")),
                    1,
                    f"{kind} 场景未被抓到：{issues}",
                )

    def test_removed_flip_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generated = self._build_synthetic_packages(root)
            # 把 B 包被翻转事实改成与 A 相同，翻转消失，B 包不再是另一个状态。
            self._rewrite_file(
                generated / "X01_state_B/STATE.md",
                lambda text: text.replace(
                    "- [F2] Credit amount: 1,900.",
                    "- [F2] Credit amount: 2,000.",
                ),
            )

            issues = self._verify(generated, cases=SYNTHETIC_CASES)

        self.assertGreaterEqual(
            len(self._issues_for(issues, "X01", "applicability_pair_state")), 1
        )

    def test_builder_rejects_generator_divergence_between_states(self):
        from benchmarks.context_integration import diagnostics

        original = diagnostics._state_work_order
        counter = {"n": 0}

        def diverging_work_order(case):
            counter["n"] += 1
            return original(case) + f"\nVariant hint #{counter['n']}\n"

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _build_synthetic_handbook(root, [("synthetic_source", "Policy.txt")])
            with mock.patch.object(
                diagnostics, "_state_work_order", side_effect=diverging_work_order
            ):
                with self.assertRaises(RuntimeError):
                    diagnostics.build_diagnostic_tasks(
                        root / "handbook",
                        root / "generated",
                        cases=SYNTHETIC_CASES,
                    )


if __name__ == "__main__":
    unittest.main()
