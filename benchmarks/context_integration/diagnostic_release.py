"""诊断层（Recall / Applicability）匿名发布闭环。

把 7 个冻结母任务 × 3 个诊断条件（policy = Recall，state_A / state_B =
Applicability A/B）共 21 个任务包导出为匿名 ZIP，并生成：

- 匿名命名：沿用 Local/Full 发布流程的 ``job-<12 位十六进制>`` 不可解读
  编号（见 ``s01_credit_memo/release_bundle.py``），文件名和包内容不得出现
  题号（S01-S10）、母任务名、研究线名、条件名（state_A、recall 等）和
  来源任务 ID；
- 私下对应表：匿名包名 → 真实母任务/条件，保存在发布目录之外的私有位置，
  格式对齐 ``experiments/next-samples-release-check/private/mapping.json``；
- 校验值：每个 ZIP 的 SHA-256 清单（``SHA256SUMS.txt``，复用
  ``build_release_bundle``）；
- 泄漏扫描：逐包扫描全部文件名和文本内容，检测题号、条件名、研究线名、
  登记表内部字段（``source_task``）和答案线索（``expected_action``、
  “correct answer” 等）。动作选项本身是题目的一部分，必须保留，不在
  扫描范围内。

校验值只证明内容是否改变，不证明包内没有泄题；泄漏扫描和人工抽查仍是
独立要求（见 docs/experiment-records.md 第 6.2 节）。
"""

from __future__ import annotations

import argparse
import json
import secrets
import shutil
import tempfile
from pathlib import Path
from typing import Mapping

from .diagnostics import build_diagnostic_tasks, load_diagnostic_cases
from .s01_credit_memo.blind_export import FORBIDDEN_MARKERS, LeakageError
from .s01_credit_memo.release_bundle import build_release_bundle


# 诊断条件名，对应登记表生成键 "{case_id}:policy" / "{case_id}:state_A/B"。
DIAGNOSTIC_CONDITIONS = ("policy", "state_A", "state_B")

# 题号标记：7 个冻结母任务的编号本身（大小写在扫描时统一处理）。
_CASE_ID_MARKERS = tuple(f"s{num:02d}" for num in (1, 2, 4, 7, 8, 9, 10))

# 诊断层特有敏感标记；通用标记复用 blind_export.FORBIDDEN_MARKERS。
DIAGNOSTIC_FORBIDDEN_MARKERS = (
    *_CASE_ID_MARKERS,
    # 研究线与诊断层名称。
    "context_integration",
    "context-integration",
    "diagnostic",
    "recall",
    "applicability",
    # 条件名。"policy" 一词本身是题目词汇（POLICY.md / 工作单），不在此列；
    # 条件映射只存在于私下对应表中。
    "state_a",
    "state_b",
    # 登记表内部字段、来源任务键和答案/评分线索。动作选项是题目的一部分，
    # 不视为泄漏。
    "source_task",
    "expected_action",
    "expected_answer",
    "correct answer",
    "correct_answer",
    "answer_key",
    "rubrics",
)

_LEAK_MARKERS = FORBIDDEN_MARKERS + DIAGNOSTIC_FORBIDDEN_MARKERS


def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def scan_diagnostic_package(package_dir: str | Path) -> None:
    """扫描一个诊断任务包的全部文件名和文本内容，发现敏感标记即报错。

    文件名逐段检查；文本文件按 UTF-8 读取后整体检查，无法解码的二进制文件
    （真实 HANDBOOK 的 .docx / .pdf 规则文件）跳过内容扫描，但其文件名仍被
    检查。任何命中都抛出 ``LeakageError``，不做静默裁剪。
    """
    package = Path(package_dir)
    for path in package.rglob("*"):
        rel = path.relative_to(package).as_posix()
        lowered_rel = rel.lower()
        for marker in _LEAK_MARKERS:
            if marker in lowered_rel:
                raise LeakageError(
                    f"forbidden marker {marker!r} in diagnostic package path: {rel}"
                )
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            continue
        for marker in _LEAK_MARKERS:
            if marker in text:
                raise LeakageError(
                    f"forbidden marker {marker!r} in diagnostic package file: {rel}"
                )


def export_diagnostic_task(
    task_dir: str | Path,
    public_root: str | Path,
    *,
    run_id: str | None = None,
) -> Path:
    """把一个诊断任务包原样复制到匿名目录，扫描通过后返回该目录。

    诊断包目录（``{case_id}_policy`` / ``{case_id}_state_{A,B}``）由
    ``build_diagnostic_tasks`` 生成，内部本来就只含模型可见文件
    （SYSTEM.md、WORK_ORDER.md、POLICY.md、STATE.md、reference/），因此直接
    整目录复制；匿名目录名使用 ``job-<随机十六进制>``，不含任何题号或条件。
    扫描失败时删除已复制的目录并向上抛错。
    """
    source = Path(task_dir).resolve()
    root = Path(public_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_id = run_id or f"job-{secrets.token_hex(6)}"
    lowered = run_id.lower()
    for marker in _LEAK_MARKERS:
        if marker in lowered:
            raise ValueError(
                f"public run_id must not reveal case or condition: {run_id!r}"
            )
    dest = root / run_id
    if dest.exists():
        raise FileExistsError(dest)
    shutil.copytree(source, dest)
    try:
        scan_diagnostic_package(dest)
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        raise
    return dest


def build_diagnostic_release(
    handbook_dir: str | Path,
    release_dir: str | Path,
    private_manifest: str | Path,
    *,
    cases: Mapping[str, Mapping] | None = None,
) -> list[Path]:
    """生成 21 个匿名诊断任务 ZIP、私下对应表和 SHA-256 清单。

    真实来源文件位于外部 HANDBOOK 仓库；``handbook_dir`` 指向该工作区。
    私下对应表必须位于发布目录之外。任一环节失败都抛错，不产出半成品清单。
    """
    if cases is None:
        cases = load_diagnostic_cases()
    handbook = Path(handbook_dir).resolve()
    release = Path(release_dir).resolve()
    manifest = Path(private_manifest).resolve()
    if _is_relative_to(manifest, release):
        raise ValueError("private manifest must be outside the release directory")

    records: dict[str, dict[str, str]] = {}
    with tempfile.TemporaryDirectory(prefix="diagnostics-release-build-") as td:
        scratch = Path(td)
        generated = scratch / "generated"
        public = scratch / "public"
        tasks = build_diagnostic_tasks(handbook, generated, cases=cases)
        expected_keys = {
            f"{case_id}:{condition}"
            for case_id in cases
            for condition in DIAGNOSTIC_CONDITIONS
        }
        if set(tasks) != expected_keys:
            raise RuntimeError(
                f"diagnostic builder did not produce all 21 packages: {sorted(tasks)}"
            )
        for key, task_dir in tasks.items():
            case_id, condition = key.split(":")
            package = export_diagnostic_task(task_dir, public)
            records[f"{package.name}.zip"] = {
                "case": case_id,
                "condition": condition,
            }
        assets = build_release_bundle(public, release)

    if set(records) != {asset.name for asset in assets}:
        raise RuntimeError("private mapping does not match generated release files")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"release_files": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return assets


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Build 21 anonymous diagnostic task ZIP files (Recall / Applicability)"
    )
    parser.add_argument("--handbook", required=True)
    parser.add_argument("--release-output", required=True)
    parser.add_argument("--private-manifest", required=True)
    args = parser.parse_args()
    assets = build_diagnostic_release(
        args.handbook, args.release_output, args.private_manifest
    )
    for asset in assets:
        print(asset)
    print(Path(args.release_output).resolve() / "SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
