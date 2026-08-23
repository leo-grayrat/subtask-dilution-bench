from __future__ import annotations

import shutil
from pathlib import Path
from typing import Mapping


SYSTEM_TEXT = (
    "You are an operations analyst. Read the work order and the supplied materials, "
    "then create the requested answer file.\n"
)


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
    cases: Mapping[str, Mapping],
) -> dict[str, Path]:
    handbook = Path(handbook_dir)
    output = Path(output_root)
    tasks: dict[str, Path] = {}

    for case_id, case in cases.items():
        source_workspace = (
            handbook
            / "tasks"
            / str(case["source_task"])
            / "environment"
            / "initial_workspace"
        )

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

    return tasks
