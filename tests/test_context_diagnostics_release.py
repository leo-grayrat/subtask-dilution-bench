import hashlib
import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

from benchmarks.context_integration.diagnostics import load_diagnostic_cases


OPAQUE_ZIP_RE = re.compile(r"^job-[0-9a-f]{12}\.zip$")
CASE_IDS = tuple(load_diagnostic_cases())
EXPECTED_CONDITIONS = ("policy", "state_A", "state_B")


def _build_synthetic_handbook(root: Path) -> Path:
    """按登记表 source_task/policy_files 构造合成 HANDBOOK 来源文件。

    真实 HANDBOOK 仓库不在本仓库内，工程测试沿用既有做法用合成来源文件
    驱动生成流程（见 tests/test_context_diagnostics.py）。
    """
    handbook = root / "handbook"
    for case in load_diagnostic_cases().values():
        for filename in case["policy_files"]:
            policy = (
                handbook
                / "tasks"
                / case["source_task"]
                / "environment"
                / "initial_workspace"
                / filename
            )
            policy.parent.mkdir(parents=True, exist_ok=True)
            policy.write_text(f"Policy source: {filename}\n", encoding="utf-8")
    return handbook


def _build_generated_tasks(root: Path):
    from benchmarks.context_integration.diagnostics import build_diagnostic_tasks

    handbook = _build_synthetic_handbook(root)
    return build_diagnostic_tasks(handbook, root / "generated")


class DiagnosticReleaseTests(unittest.TestCase):
    """21 个匿名 ZIP、私下对应表和校验值的发布闭环。"""

    def test_release_creates_21_anonymous_zips_with_mapping_and_checksums(self):
        from benchmarks.context_integration.diagnostic_release import (
            build_diagnostic_release,
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = _build_synthetic_handbook(root)
            release = root / "release"
            manifest = root / "private/mapping.json"

            assets = build_diagnostic_release(
                handbook, release, manifest
            )

            self.assertEqual(len(assets), 21)
            self.assertEqual(
                len(list(release.glob("job-*.zip"))), 21
            )
            for asset in assets:
                self.assertTrue(
                    OPAQUE_ZIP_RE.fullmatch(asset.name),
                    f"匿名包名泄漏结构信息: {asset.name}",
                )

            # SHA-256 校验值清单覆盖全部 21 个 ZIP 且与实际字节一致。
            sums = (release / "SHA256SUMS.txt").read_text(encoding="utf-8")
            lines = [line for line in sums.splitlines() if line.strip()]
            self.assertEqual(len(lines), 21)
            recorded = {}
            for line in lines:
                digest, name = line.split("  ")
                recorded[name] = digest
            for asset in assets:
                self.assertEqual(
                    recorded[asset.name],
                    hashlib.sha256(asset.read_bytes()).hexdigest(),
                    f"{asset.name} 的校验值与实际内容不一致",
                )

            # 私下对应表不得出现在发布目录内，且覆盖全部 case × 条件。
            self.assertFalse((release / "mapping.json").exists())
            mapping = json.loads(manifest.read_text(encoding="utf-8"))[
                "release_files"
            ]
            self.assertEqual(set(mapping), {asset.name for asset in assets})
            pairs = {(record["case"], record["condition"]) for record in mapping.values()}
            self.assertEqual(
                pairs,
                {
                    (case_id, condition)
                    for case_id in CASE_IDS
                    for condition in EXPECTED_CONDITIONS
                },
            )

    def test_zip_contents_hide_case_condition_and_registry_identity(self):
        from benchmarks.context_integration.diagnostic_release import (
            build_diagnostic_release,
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = _build_synthetic_handbook(root)
            assets = build_diagnostic_release(
                handbook, root / "release", root / "private/mapping.json"
            )

            forbidden = [
                "s01", "s02", "s04", "s07", "s08", "s09", "s10",
                "state_a", "state_b", "recall", "applicability",
                "diagnostic", "source_task", "expected_action",
            ]
            for asset in assets:
                with zipfile.ZipFile(asset) as archive:
                    for name in archive.namelist():
                        lowered = name.lower()
                        for marker in forbidden:
                            self.assertNotIn(
                                marker,
                                lowered,
                                f"{asset.name} 内文件名 {name} 含敏感标记 {marker}",
                            )
                    for name in archive.namelist():
                        text = archive.read(name).decode("utf-8").lower()
                        for marker in forbidden:
                            self.assertNotIn(
                                marker,
                                text,
                                f"{asset.name} 内 {name} 含敏感标记 {marker}",
                            )

    def test_legitimate_action_options_survive_release_scan(self):
        """动作选项本身是题目的一部分，发布流程不得把它们当泄漏裁剪。"""
        from benchmarks.context_integration.diagnostic_release import (
            build_diagnostic_release,
        )

        cases = load_diagnostic_cases()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handbook = _build_synthetic_handbook(root)
            manifest = root / "private/mapping.json"
            assets = build_diagnostic_release(handbook, root / "release", manifest)
            mapping = json.loads(manifest.read_text(encoding="utf-8"))[
                "release_files"
            ]

            for asset in assets:
                record = mapping[asset.name]
                case = cases[record["case"]]
                options = case["rule"]["action_options"]
                with zipfile.ZipFile(asset) as archive:
                    work_order = archive.read("WORK_ORDER.md").decode("utf-8")
                for option in options:
                    self.assertIn(
                        option,
                        work_order,
                        f"{asset.name} 的工作单丢失动作选项 {option}",
                    )

    def test_private_manifest_inside_release_is_rejected(self):
        from benchmarks.context_integration.diagnostic_release import (
            build_diagnostic_release,
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                build_diagnostic_release(
                    root / "handbook",
                    root / "release",
                    root / "release/mapping.json",
                )


class DiagnosticLeakScanTests(unittest.TestCase):
    """泄漏扫描必须抓到题号、条件名、来源任务与答案字段，且不误伤正常内容。"""

    def _scan_directory(self, path):
        from benchmarks.context_integration.diagnostic_release import (
            scan_diagnostic_package,
        )

        scan_diagnostic_package(path)

    def _build_one_state_package(self, root: Path) -> Path:
        tasks = _build_generated_tasks(root)
        return tasks["S01:state_A"]

    def test_clean_packages_pass_the_leak_scan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tasks = _build_generated_tasks(root)
            self.assertEqual(len(tasks), 21)
            for task_dir in tasks.values():
                self._scan_directory(task_dir)

    def test_case_id_in_content_is_rejected(self):
        leaks = {
            "case_id": "This follows up on S04 from the last batch.\n",
            "lowercase_case_id": "see s07 for the earlier version.\n",
        }
        for kind, leak in leaks.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    package = self._build_one_state_package(root)
                    (package / "STATE.md").write_text(
                        (package / "STATE.md").read_text(encoding="utf-8") + leak,
                        encoding="utf-8",
                    )
                    with self.assertRaises(Exception) as ctx:
                        self._scan_directory(package)
                    self.assertEqual(type(ctx.exception).__name__, "LeakageError")

    def test_condition_and_layer_names_in_content_are_rejected(self):
        leaks = {
            "condition_name": "Compare against state_B before answering.\n",
            "layer_name_recall": "This is the recall probe.\n",
            "layer_name_applicability": "This is the applicability probe.\n",
            "research_line": "Built for context_integration.\n",
        }
        for kind, leak in leaks.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    package = self._build_one_state_package(root)
                    (package / "POLICY.md").write_text(
                        (package / "POLICY.md").read_text(encoding="utf-8") + leak,
                        encoding="utf-8",
                    )
                    with self.assertRaises(Exception) as ctx:
                        self._scan_directory(package)
                    self.assertEqual(type(ctx.exception).__name__, "LeakageError")

    def test_answer_and_registry_fields_in_content_are_rejected(self):
        leaks = {
            "expected_action": '"expected_action": "dispute"\n',
            "answer_phrase": "The correct answer is dispute.\n",
            "source_task": "source_task: finance_meridian_partners_158b9045\n",
            "scorer_file": "Run result_scorer.py after grading.\n",
        }
        for kind, leak in leaks.items():
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    package = self._build_one_state_package(root)
                    (package / "WORK_ORDER.md").write_text(
                        (package / "WORK_ORDER.md").read_text(encoding="utf-8")
                        + leak,
                        encoding="utf-8",
                    )
                    with self.assertRaises(Exception) as ctx:
                        self._scan_directory(package)
                    self.assertEqual(type(ctx.exception).__name__, "LeakageError")

    def test_leaking_filename_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = self._build_one_state_package(root)
            (package / "S04_notes.md").write_text("clean body\n", encoding="utf-8")
            with self.assertRaises(Exception) as ctx:
                self._scan_directory(package)
            self.assertEqual(type(ctx.exception).__name__, "LeakageError")

    def test_export_rejects_leaking_package_and_cleans_up(self):
        from benchmarks.context_integration.diagnostic_release import (
            export_diagnostic_task,
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = self._build_one_state_package(root)
            (package / "HINT.md").write_text(
                "The expected_action is dispute.\n", encoding="utf-8"
            )
            public = root / "public"
            with self.assertRaises(Exception) as ctx:
                export_diagnostic_task(
                    package, public, run_id="job-0123456789ab"
                )
            self.assertEqual(type(ctx.exception).__name__, "LeakageError")
            self.assertFalse((public / "job-0123456789ab").exists())


if __name__ == "__main__":
    unittest.main()
