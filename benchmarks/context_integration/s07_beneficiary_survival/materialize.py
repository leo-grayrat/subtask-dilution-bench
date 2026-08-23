from __future__ import annotations

import json
import shutil
from pathlib import Path


ISSUE_KEY = "CLM_LIFE-3"
EVIDENCE_FILE = "additional_document_drummond_01.pdf"
POLICY_FILE = "Policy_LC-2018-06231_Declarations.pdf"
INSURED_DEATH_FILE = "Death_Certificate_Drummond_Harold.pdf"
LOCAL_INSTRUCTION = (
    "Process only life claim CLM_LIFE-3. Read the claim attachments, the files in the current "
    "workspace, and the Life Claims SOP. Complete every action required for this claim.\n"
)


def _allocation_verifier(variant: str) -> str:
    expected = {
        "A": [
            ("mark", "63.64%", ("381,818.18", "381818.18")),
            ("susan", "36.36%", ("218,181.82", "218181.82")),
        ],
        "B": [
            ("linda", "45%", ("270,000.00", "270000.00", "270,000")),
            ("mark", "35%", ("210,000.00", "210000.00", "210,000")),
            ("susan", "20%", ("120,000.00", "120000.00", "120,000")),
        ],
    }[variant]
    return f'''from pathlib import Path
import json
import re

EXPECTED = {expected!r}
VARIANT = {variant!r}

def _text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        own = str(node.get("text", "")) if node.get("type") == "text" else ""
        return own + " ".join(_text(child) for child in node.get("content", []))
    if isinstance(node, list):
        return " ".join(_text(item) for item in node)
    return ""

def _comments(data, issue):
    parts = []
    for comment in data.get("comments", {{}}).get("CLM_LIFE-3", []):
        parts.append(_text(comment.get("body", comment)) if isinstance(comment, dict) else _text(comment))
    fields = issue.get("fields", {{}})
    comment_field = fields.get("comment", {{}}) if isinstance(fields, dict) else {{}}
    if isinstance(comment_field, dict):
        for comment in comment_field.get("comments", []):
            parts.append(_text(comment.get("body", comment)) if isinstance(comment, dict) else _text(comment))
    return "\\n".join(parts)

def _segment(text, name):
    lower = text.lower()
    pos = lower.find(name)
    if pos < 0:
        return ""
    return lower[pos:pos + 180]

def _status(issue):
    fields = issue.get("fields", {{}}) if isinstance(issue, dict) else {{}}
    value = fields.get("status", "") if isinstance(fields, dict) else ""
    if isinstance(value, dict):
        return str(value.get("name", ""))
    return str(value)

def verify(workspace_path, external_services_path=None):
    if external_services_path is None:
        return {{"pass": False, "score": 0.0, "feedback": "external services path missing"}}
    path = Path(external_services_path) / "jira_state.json"
    if not path.exists():
        return {{"pass": False, "score": 0.0, "feedback": "jira_state.json not found"}}
    data = json.loads(path.read_text(encoding="utf-8"))
    issues = data.get("issues", {{}}) if isinstance(data, dict) else {{}}
    issue = issues.get("CLM_LIFE-3") if isinstance(issues, dict) else None
    if not isinstance(issue, dict):
        return {{"pass": False, "score": 0.0, "feedback": "CLM_LIFE-3 not found"}}

    failures = []
    status = _status(issue).lower()
    fields = issue.get("fields", {{}})
    labels = [str(x).lower() for x in fields.get("labels", [])] if isinstance(fields, dict) else []
    if "route to ap for payout" not in status:
        failures.append("claim was not routed to AP for payout")
    hold_text = " ".join([status] + labels)
    if "clm-910" in hold_text or "clm-920" in hold_text or "hold" in status:
        failures.append("claim has an incorrect hold")

    comments = _comments(data, issue)
    lower = comments.lower()
    if "beneficiary" not in lower or "allocation" not in lower:
        failures.append("beneficiary allocation comment missing")
    if "lc-2018-06231" not in lower:
        failures.append("policy number missing")
    if not any(token in comments for token in ("600,000.00", "600000.00", "600,000")):
        failures.append("face amount missing")
    if "analyst" not in lower or not re.search(r"202[0-9]", lower):
        failures.append("analyst and date attribution missing")

    for name, percent, amounts in EXPECTED:
        segment = _segment(comments, name)
        if not segment:
            failures.append(f"{{name}} allocation missing")
            continue
        compact = segment.replace(" ", "")
        if percent.replace(" ", "") not in compact:
            failures.append(f"{{name}} percentage incorrect")
        if not any(amount in segment or amount.replace(",", "") in segment.replace(",", "") for amount in amounts):
            failures.append(f"{{name}} amount incorrect")

    exclusion_words = ("exclud", "not included", "not payable", "no payout", "contingent")
    for name in (("linda", "george") if VARIANT == "A" else ("george",)):
        segment = _segment(comments, name)
        if segment and not any(word in segment for word in exclusion_words):
            failures.append(f"{{name}} was incorrectly included as a payee")

    return {{
        "pass": not failures,
        "score": 1.0 if not failures else 0.0,
        "feedback": "ok" if not failures else "; ".join(failures),
    }}
'''


def _target_rubric(variant: str) -> dict:
    if variant == "A":
        expectation = (
            "Linda died before the insured, so exclude Linda and contingent beneficiary George; "
            "redistribute the benefit to Mark (63.64%, $381,818.18) and Susan (36.36%, $218,181.82)."
        )
    else:
        expectation = (
            "No evidence shows a primary beneficiary died before the insured, so allocate Linda "
            "45%/$270,000, Mark 35%/$210,000, and Susan 20%/$120,000; exclude contingent George."
        )
    return {
        "id": "S07-ALLOCATION",
        "sort_order": 100,
        "rubric_text": (
            f"For CLM_LIFE-3, {expectation} Add the structured allocation comment and route the "
            "claim to AP for payout without CLM-910 or CLM-920."
        ),
        "verifier_code": _allocation_verifier(variant),
        "criterion_type": "expected_output",
    }


def _jira_path(task: Path) -> Path:
    return task / "environment/initial_external_services/jira/jira_state.json"


def _validate_and_find_attachment(task: Path) -> tuple[Path, dict, list, int]:
    workspace = task / "environment/initial_workspace"
    for filename in (POLICY_FILE, INSURED_DEATH_FILE, EVIDENCE_FILE):
        if not (workspace / filename).is_file():
            raise RuntimeError(f"required source file missing: {filename}")

    path = _jira_path(task)
    data = json.loads(path.read_text(encoding="utf-8"))
    issue = data.get("issues", {}).get(ISSUE_KEY)
    if not isinstance(issue, dict):
        raise RuntimeError(f"{ISSUE_KEY} missing from Jira source")
    attachments = issue.get("fields", {}).get("attachment")
    if not isinstance(attachments, list):
        raise RuntimeError(f"{ISSUE_KEY} attachment list missing")
    matches = [i for i, item in enumerate(attachments) if item.get("filename") == EVIDENCE_FILE]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {EVIDENCE_FILE} attachment, found {len(matches)}")
    return path, data, attachments, matches[0]


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

    jira_path, jira, attachments, evidence_index = _validate_and_find_attachment(output)
    if variant == "B":
        (output / "environment/initial_workspace" / EVIDENCE_FILE).unlink()
        del attachments[evidence_index]
        jira_path.write_text(json.dumps(jira, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if mode == "local":
        (output / "instruction.md").write_text(LOCAL_INSTRUCTION, encoding="utf-8")

    rubrics_path = output / "tests/rubrics.json"
    rubrics = json.loads(rubrics_path.read_text(encoding="utf-8"))
    target = _target_rubric(variant)
    if mode == "local":
        rubrics = [target]
    else:
        rubrics = [
            rubric for rubric in rubrics
            if ISSUE_KEY.lower() not in str(rubric.get("rubric_text", "")).lower()
        ]
        rubrics.append(target)
    rubrics_path.write_text(json.dumps(rubrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build S07 HANDBOOK local/full A/B task variants")
    parser.add_argument("source_task_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--mode", choices=["local", "full"], required=True)
    parser.add_argument("--variant", choices=["A", "B"], required=True)
    args = parser.parse_args()
    materialize(args.source_task_dir, args.output_dir, mode=args.mode, variant=args.variant)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
