from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Mapping


SYSTEM_TEXT = (
    "You are an operations analyst. Read the work order and the supplied materials, "
    "then create the requested answer file.\n"
)
REGISTRY_PATH = Path(__file__).with_name("diagnostic_cases.json")


def load_diagnostic_cases(path: str | Path = REGISTRY_PATH) -> dict[str, dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_diagnostic_registry(
    cases: Mapping[str, Mapping] | None = None,
    *,
    handbook_dir: str | Path | None = None,
) -> list[dict]:
    """校验诊断登记表的四条不变量，返回违规列表，空列表表示全部通过。

    四条不变量（见 HANDOFF-2026-08-25.md 与 docs/context-integration/design.md 第 4 节）：
    1. ``source_files``：登记表引用的每个来源文件在 HANDBOOK 工作区内真实存在；
    2. ``action_flip``：A/B 目标动作互为相反，且正好覆盖两个允许动作；
    3. ``allowed_actions``：``when_true`` / ``when_false`` / ``expected_action``
       均属于该母任务声明的允许集合 ``rule.action_options``；
    4. ``single_flipped_fact``：A/B 使用同一组事实编号，未翻转事实逐字一致，
       至少翻转一个事实，且每个被翻转的事实都声明为支撑事实。
       设计允许同一关键业务事实的多个重复表示同步修改，机械校验无法判定
       多个翻转事实是否属于同一业务事实，逐题语义复核仍需人工完成。

    不传 ``handbook_dir`` 时不检查第 1 条，因为来源文件位于外部 HANDBOOK 仓库。
    """
    if cases is None:
        cases = load_diagnostic_cases()
    issues: list[dict] = []

    def add(case_id: str, invariant: str, message: str) -> None:
        issues.append({"case": case_id, "invariant": invariant, "message": message})

    handbook = Path(handbook_dir) if handbook_dir is not None else None

    for case_id, case in cases.items():
        rule = case.get("rule", {})
        states = case.get("states", {})

        # 不变量 1：来源文件存在。
        if handbook is not None:
            workspace = _source_workspace(handbook, case)
            for filename in case.get("policy_files", []):
                source = workspace / str(filename)
                if not source.is_file():
                    add(case_id, "source_files", f"missing source file: {source}")

        # 不变量 3：动作属于该母任务声明的允许集合。
        options = list(rule.get("action_options", []))
        allowed = set(options)
        for field in ("when_true", "when_false"):
            value = rule.get(field)
            if value not in allowed:
                add(
                    case_id,
                    "allowed_actions",
                    f"rule.{field}={value!r} is not in action_options {sorted(allowed)!r}",
                )
        for state_id, state in states.items():
            value = state.get("expected_action")
            if value not in allowed:
                add(
                    case_id,
                    "allowed_actions",
                    f"states.{state_id}.expected_action={value!r} "
                    f"is not in action_options {sorted(allowed)!r}",
                )

        # 不变量 2：A/B 动作真正翻转。
        if len(options) != 2 or len(allowed) != 2:
            add(
                case_id,
                "action_flip",
                f"action_options must list exactly two distinct actions, got {options!r}",
            )
        if rule.get("when_true") == rule.get("when_false"):
            add(case_id, "action_flip", "when_true and when_false must be opposite actions")
        if set(states) != {"A", "B"}:
            add(case_id, "action_flip", f"states must be exactly A and B, got {sorted(states)!r}")
            continue
        action_a = states["A"].get("expected_action")
        action_b = states["B"].get("expected_action")
        if action_a == action_b:
            add(
                case_id,
                "action_flip",
                f"states A and B share the same expected action {action_a!r}; "
                "the correct action must flip",
            )
        elif set(states) == {"A", "B"} and len(allowed) == 2 and {action_a, action_b} != allowed:
            add(
                case_id,
                "action_flip",
                f"A/B actions {{{action_a!r}, {action_b!r}}} do not cover "
                f"both allowed actions {sorted(allowed)!r}",
            )

        # 不变量 4：只翻转单一关键业务事实。
        facts_a = {fact["id"]: fact["text"] for fact in states["A"].get("facts", [])}
        facts_b = {fact["id"]: fact["text"] for fact in states["B"].get("facts", [])}
        if set(facts_a) != set(facts_b):
            only_a = sorted(set(facts_a) - set(facts_b))
            only_b = sorted(set(facts_b) - set(facts_a))
            add(
                case_id,
                "single_flipped_fact",
                f"fact id sets differ between A and B; only in A: {only_a}, only in B: {only_b}",
            )
            continue
        changed = [fid for fid in facts_a if facts_a[fid] != facts_b[fid]]
        if not changed:
            add(case_id, "single_flipped_fact", "no fact is flipped between states A and B")
        for state_id in ("A", "B"):
            supporting = set(states[state_id].get("supporting_fact_ids", []))
            unknown = sorted(supporting - set(facts_a))
            if unknown:
                add(
                    case_id,
                    "single_flipped_fact",
                    f"state {state_id} supporting_fact_ids reference unknown facts {unknown}",
                )
            undeclared = [fid for fid in changed if fid not in supporting]
            if undeclared:
                add(
                    case_id,
                    "single_flipped_fact",
                    f"state {state_id}: flipped facts {undeclared} are not declared "
                    "as supporting facts; a second fact may have changed silently",
                )

    return issues


def _source_workspace(handbook: Path, case: Mapping) -> Path:
    return (
        handbook
        / "tasks"
        / str(case.get("source_task", ""))
        / "environment"
        / "initial_workspace"
    )


def sha256_file(path: str | Path) -> str:
    """计算文件的 SHA-256 摘要，用于证明材料完整性。"""
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_recall_package_integrity(
    output_root: str | Path,
    handbook_dir: str | Path,
    *,
    cases: Mapping[str, Mapping] | None = None,
) -> list[dict]:
    """校验 Recall 任务包携带的规则文件与来源文件逐字节一致，返回违规列表。

    Recall 包（``{case_id}_policy``）把登记表 ``policy_files`` 列出的来源规则文件
    复制进 ``reference/``。本函数逐文件用 SHA-256 比对，证明包内内容完整、
    未被改写、未被截断（见 HANDOFF-2026-08-25.md 第 4 节未完成项第 3 条）。
    三类违规：
    1. ``recall_source_file``：来源文件在 HANDBOOK 工作区内不存在；
    2. ``recall_package_file``：Recall 包内缺少应有的规则文件；
    3. ``recall_sha256``：包内文件与来源文件的 SHA-256 不一致。
    任何缺失都显式报告而不是静默通过；空列表表示全部通过。
    """
    if cases is None:
        cases = load_diagnostic_cases()
    issues: list[dict] = []

    def add(case_id: str, invariant: str, message: str) -> None:
        issues.append({"case": case_id, "invariant": invariant, "message": message})

    handbook = Path(handbook_dir)
    output = Path(output_root)

    for case_id, case in cases.items():
        workspace = _source_workspace(handbook, case)
        reference = output / f"{case_id}_policy" / "reference"
        for filename in case.get("policy_files", []):
            name = Path(str(filename)).name
            source = workspace / str(filename)
            copied = reference / name
            if not source.is_file():
                add(case_id, "recall_source_file", f"missing source file: {source}")
                continue
            if not copied.is_file():
                add(case_id, "recall_package_file", f"missing package file: {copied}")
                continue
            source_hash = sha256_file(source)
            copied_hash = sha256_file(copied)
            if source_hash != copied_hash:
                add(
                    case_id,
                    "recall_sha256",
                    f"{name}: package sha256 {copied_hash} does not match "
                    f"source sha256 {source_hash}",
                )

    return issues


def _reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def _write_common_files(path: Path, work_order: str) -> None:
    (path / "SYSTEM.md").write_text(SYSTEM_TEXT, encoding="utf-8")
    (path / "WORK_ORDER.md").write_text(work_order, encoding="utf-8")


def _policy_work_order(case: Mapping) -> str:
    rule = case["rule"]
    conditions = ", ".join(f"`{value}`" for value in rule["condition_options"])
    actions = ", ".join(f"`{value}`" for value in rule["action_options"])
    return (
        "# Work order\n\n"
        f"Use the complete materials in `reference/` to identify the policy controlling "
        f"{case['subject']}.\n\n"
        f"Allowed condition codes: {conditions}.\n\n"
        f"Allowed action codes: {actions}.\n\n"
        "Create `answer.json` in this directory with exactly these fields:\n\n"
        "```json\n"
        "{\n"
        '  "condition": "<one allowed condition code>",\n'
        '  "when_true": "<one allowed action code>",\n'
        '  "when_false": "<one allowed action code>",\n'
        '  "source_file": "<reference filename>",\n'
        '  "rule_summary": "<brief explanation in your own words>"\n'
        "}\n"
        "```\n"
    )


def _state_work_order(case: Mapping) -> str:
    actions = ", ".join(f"`{value}`" for value in case["rule"]["action_options"])
    return (
        "# Work order\n\n"
        f"Read `POLICY.md` and `STATE.md`, then decide the correct action for "
        f"{case['subject']}.\n\n"
        f"Allowed action codes: {actions}.\n\n"
        "Create `answer.json` in this directory with exactly these fields:\n\n"
        "```json\n"
        "{\n"
        '  "action": "<one allowed action code>",\n'
        '  "supporting_fact_ids": ["<fact id>"],\n'
        '  "reasoning": "<brief explanation>"\n'
        "}\n"
        "```\n"
    )


def build_diagnostic_tasks(
    handbook_dir: str | Path,
    output_root: str | Path,
    *,
    cases: Mapping[str, Mapping] | None = None,
) -> dict[str, Path]:
    handbook = Path(handbook_dir)
    output = Path(output_root)
    if cases is None:
        cases = load_diagnostic_cases()
    tasks: dict[str, Path] = {}

    for case_id, case in cases.items():
        source_workspace = _source_workspace(handbook, case)

        policy_task = output / f"{case_id}_policy"
        _reset_directory(policy_task)
        _write_common_files(policy_task, _policy_work_order(case))
        reference = policy_task / "reference"
        reference.mkdir()
        for filename in case["policy_files"]:
            source = source_workspace / str(filename)
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copy2(source, reference / source.name)
        tasks[f"{case_id}:policy"] = policy_task

        for state_id, state in case["states"].items():
            state_task = output / f"{case_id}_state_{state_id}"
            _reset_directory(state_task)
            _write_common_files(state_task, _state_work_order(case))
            (state_task / "POLICY.md").write_text(
                "# Relevant policy\n\n" + str(case["rule"]["text"]) + "\n",
                encoding="utf-8",
            )
            facts = "\n".join(
                f"- [{fact['id']}] {fact['text']}" for fact in state["facts"]
            )
            (state_task / "STATE.md").write_text(
                "# Current state\n\n" + facts + "\n",
                encoding="utf-8",
            )
            tasks[f"{case_id}:state_{state_id}"] = state_task

    # 生成时内建校验：证明 Recall 包复制的是完整原始规则文件。
    integrity = verify_recall_package_integrity(output, handbook, cases=cases)
    if integrity:
        raise RuntimeError(f"recall package integrity check failed: {integrity}")

    return tasks


def score_diagnostic_answer(
    answer_path: str | Path,
    *,
    case_id: str,
    condition: str,
    cases: Mapping[str, Mapping],
) -> dict:
    answer = json.loads(Path(answer_path).read_text(encoding="utf-8"))
    case = cases[case_id]
    if condition == "policy":
        expected = case["rule"]
        checks = {
            "condition": answer.get("condition") == expected["condition"],
            "when_true": answer.get("when_true") == expected["when_true"],
            "when_false": answer.get("when_false") == expected["when_false"],
            "source_file": answer.get("source_file") in case["policy_files"],
        }
    elif condition.startswith("state_") and condition[6:] in case["states"]:
        state = case["states"][condition[6:]]
        fact_ids = answer.get("supporting_fact_ids")
        checks = {
            "action": answer.get("action") == state["expected_action"],
            "supporting_fact_ids": isinstance(fact_ids, list)
            and set(fact_ids) == set(state["supporting_fact_ids"]),
            "reasoning": isinstance(answer.get("reasoning"), str)
            and bool(answer["reasoning"].strip()),
        }
    else:
        raise ValueError(f"unknown condition: {condition}")

    score = sum(checks.values()) / len(checks)
    return {
        "pass": all(checks.values()),
        "score": round(score, 3),
        "checks": checks,
    }
