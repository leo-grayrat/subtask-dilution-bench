from __future__ import annotations

import json
import shutil
from pathlib import Path


TARGET_ISSUE = "OPS-12"
TARGET_TRANSACTION = "SUSP-013"
ACTIVE_APPROVER = "U005"
INACTIVE_APPROVER = "U001"
LOCAL_INSTRUCTION = (
    "Process only the March suspense item SUSP-013, which is supported by Jira issue OPS-12. "
    "Follow the existing Vanguard Shield SOP, update the required reconciliation workbook, "
    "and complete every required record or escalation for this item.\n"
)


def _workbook_verifier(variant: str) -> str:
    expected_status = "EXCEPTION" if variant == "A" else "FIN-100"
    return f'''from pathlib import Path
import openpyxl

def verify(workspace_path, external_services_path=None):
    workspace = Path(workspace_path)
    target = workspace / "Suspense_Reconciliation_March2026.xlsx"
    if not target.exists():
        matches = list(workspace.glob("*Suspense*Reconciliation*.xlsx"))
        if not matches:
            return {{"pass": False, "score": 0.0, "feedback": "reconciliation workbook not found"}}
        target = matches[0]
    wb = openpyxl.load_workbook(target, data_only=False)
    row_data = None
    columns = None
    for ws in wb.worksheets:
        values = list(ws.iter_rows(values_only=True))
        if not values:
            continue
        headers = [str(x or "").strip().lower() for x in values[0]]
        def col(*names):
            for i, value in enumerate(headers):
                if any(name in value for name in names):
                    return i
            return None
        id_col = col("transaction", "susp", "item")
        status_col = col("status")
        support_col = col("support found")
        conflict_col = col("conflict")
        notes_col = col("resolution note", "notes")
        if None in (id_col, status_col, support_col, conflict_col, notes_col):
            continue
        for row in values[1:]:
            identity = str(row[id_col] or "").upper()
            if "SUSP-013" in identity or "OPS-12" in identity:
                row_data = row
                columns = (status_col, support_col, conflict_col, notes_col)
                break
        if row_data is not None:
            break
    if row_data is None:
        return {{"pass": False, "score": 0.0, "feedback": "SUSP-013 / OPS-12 row not found"}}
    status_col, support_col, conflict_col, notes_col = columns
    status = str(row_data[status_col] or "").strip().upper()
    support = str(row_data[support_col] or "").strip().upper()
    conflict = str(row_data[conflict_col] or "").strip().upper()
    notes = str(row_data[notes_col] or "").strip().lower()
    failures = []
    if support not in ("Y", "YES"):
        failures.append(f"Support Found={{support!r}}")
    if conflict not in ("N", "NO"):
        failures.append(f"Conflict={{conflict!r}}")
    if "{expected_status}" not in status:
        failures.append(f"Status={{status!r}}, expected {expected_status}")
    if "{variant}" == "A":
        if not any(x in notes for x in ("junior", "not a manager", "manager confirmation", "invalid approval", "insufficient approval")):
            failures.append("notes do not explain that junior approval is invalid")
    else:
        if not (any(x in notes for x in ("manager", "finance manager")) and any(x in notes for x in ("approval", "approved", "slack"))):
            failures.append("notes do not identify valid manager approval")
    return {{
        "pass": not failures,
        "score": 1.0 if not failures else 0.0,
        "feedback": "ok" if not failures else "; ".join(failures),
    }}
'''


def _jira_verifier(variant: str) -> str:
    return f'''from pathlib import Path
import json

def _assignee_is_jennifer(issue):
    fields = issue.get("fields", {{}}) if isinstance(issue, dict) else {{}}
    assignee = fields.get("assignee", issue.get("assignee", {{}})) if isinstance(fields, dict) else {{}}
    return "jennifer.walsh" in json.dumps(assignee).lower()

def verify(workspace_path, external_services_path=None):
    if external_services_path is None:
        return {{"pass": False, "score": 0.0, "feedback": "external services path missing"}}
    path = Path(external_services_path) / "jira_state.json"
    if not path.exists():
        return {{"pass": False, "score": 0.0, "feedback": "jira_state.json not found"}}
    data = json.loads(path.read_text(encoding="utf-8"))
    comments = data.get("comments", {{}}).get("OPS-12", []) if isinstance(data, dict) else []
    comment_text = json.dumps(comments).lower()
    issues = data.get("issues", {{}}) if isinstance(data, dict) else {{}}
    if isinstance(issues, list):
        issue_pairs = [(str(x.get("key", "")), x) for x in issues if isinstance(x, dict)]
    elif isinstance(issues, dict):
        issue_pairs = list(issues.items())
    else:
        issue_pairs = []
    target_fin = []
    for key, issue in issue_pairs:
        if str(key).upper().startswith("FIN-") and "BOARD" not in str(key).upper():
            body = (str(key) + " " + json.dumps(issue)).lower()
            if "ops-12" in body or "susp-013" in body:
                target_fin.append(issue)
    failures = []
    if "{variant}" == "A":
        if not target_fin:
            failures.append("no FIN exception ticket references OPS-12 / SUSP-013")
        elif not any(_assignee_is_jennifer(x) for x in target_fin):
            failures.append("target exception ticket is not assigned to jennifer.walsh")
        if not (any(x in comment_text for x in ("junior", "not a manager", "invalid", "insufficient")) and any(x in comment_text for x in ("exception", "escalat", "manager"))):
            failures.append("OPS-12 comment does not explain invalid approval and escalation")
        if "fin-100 cleared & posted" in comment_text:
            failures.append("OPS-12 was incorrectly cleared")
    else:
        if target_fin:
            failures.append("valid manager approval incorrectly produced a FIN exception")
        if "fin-100 cleared & posted" not in comment_text:
            failures.append("OPS-12 clearing comment missing")
        if "6600" not in comment_text:
            failures.append("OPS-12 clearing comment does not include target GL code")
    return {{
        "pass": not failures,
        "score": 1.0 if not failures else 0.0,
        "feedback": "ok" if not failures else "; ".join(failures),
    }}
'''


def _target_rubrics(variant: str) -> list[dict]:
    if variant == "A":
        route_text = "SUSP-013 / OPS-12 must remain an exception because the only approval is from a junior analyst."
        jira_text = "OPS-12 must be escalated through a FIN exception and must not be cleared."
    else:
        route_text = "SUSP-013 / OPS-12 must be FIN-100 because a valid Finance Manager approval is present."
        jira_text = "OPS-12 must be cleared and must not receive a FIN exception for missing manager approval."
    return [
        {
            "id": "S02-WORKBOOK",
            "sort_order": 100,
            "rubric_text": route_text,
            "verifier_code": _workbook_verifier(variant),
            "criterion_type": "expected_output",
        },
        {
            "id": "S02-JIRA",
            "sort_order": 101,
            "rubric_text": jira_text,
            "verifier_code": _jira_verifier(variant),
            "criterion_type": "expected_output",
        },
    ]


def _find_target_message(slack: dict) -> dict:
    matches = []
    message_groups = slack.get("messages", {})
    if not isinstance(message_groups, dict):
        message_groups = {}
    for channel_value in slack.get("channels", {}).values():
        if isinstance(channel_value, list):
            message_groups = {**message_groups, f"legacy-{len(message_groups)}": channel_value}
    for messages in message_groups.values():
        if not isinstance(messages, list):
            continue
        for message in messages:
            if not isinstance(message, dict):
                continue
            text = str(message.get("text") or "")
            if "OPS-12" in text and "7,500" in text and "Approved" in text:
                matches.append(message)
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one OPS-12 $7,500 approval message, found {len(matches)}")
    return matches[0]


def materialize(source_task_dir: str | Path, output_dir: str | Path, *, mode: str, variant: str) -> None:
    if mode not in {"local", "full"}:
        raise ValueError("mode must be 'local' or 'full'")
    if variant not in {"A", "B"}:
        raise ValueError("variant must be 'A' or 'B'")

    source = Path(source_task_dir)
    output = Path(output_dir)
    if not source.is_dir():
        raise FileNotFoundError(source)
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output)

    slack_path = output / "environment/initial_external_services/slack/slack.json"
    slack = json.loads(slack_path.read_text(encoding="utf-8"))
    target = _find_target_message(slack)
    expected_author = ACTIVE_APPROVER if variant == "A" else INACTIVE_APPROVER
    if variant == "A" and target.get("user") != ACTIVE_APPROVER:
        raise RuntimeError(f"variant A source approval author is {target.get('user')!r}, expected {ACTIVE_APPROVER}")
    if variant == "B":
        if target.get("user") != ACTIVE_APPROVER:
            raise RuntimeError(f"cannot flip approval author from {target.get('user')!r}")
        target["user"] = INACTIVE_APPROVER
    if expected_author not in slack.get("users", {}):
        raise RuntimeError(f"approval user {expected_author} missing from Slack users")
    slack_path.write_text(json.dumps(slack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if mode == "local":
        (output / "instruction.md").write_text(LOCAL_INSTRUCTION, encoding="utf-8")

    rubrics_path = output / "tests/rubrics.json"
    rubrics = json.loads(rubrics_path.read_text(encoding="utf-8"))
    target_rubrics = _target_rubrics(variant)
    if mode == "local":
        rubrics = target_rubrics
    else:
        rubrics = [r for r in rubrics if "OPS-12" not in str(r.get("rubric_text", "")).upper()]
        rubrics.extend(target_rubrics)
    rubrics_path.write_text(json.dumps(rubrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build S02 HANDBOOK local/full A/B task variants")
    parser.add_argument("source_task_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--mode", choices=["local", "full"], required=True)
    parser.add_argument("--variant", choices=["A", "B"], required=True)
    args = parser.parse_args()
    materialize(args.source_task_dir, args.output_dir, mode=args.mode, variant=args.variant)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
