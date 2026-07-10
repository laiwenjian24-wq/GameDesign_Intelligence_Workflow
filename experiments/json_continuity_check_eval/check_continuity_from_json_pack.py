"""Run minimal continuity checks from a JSON Context Pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from .claim_schema import Claim, ContinuityIssue
    from .continuity_rules import check_claims_against_context_pack, decision_from_issues
    from .simple_claim_extractor import extract_claims
except ImportError:  # pragma: no cover - direct script execution
    from claim_schema import Claim, ContinuityIssue
    from continuity_rules import check_claims_against_context_pack, decision_from_issues
    from simple_claim_extractor import extract_claims


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTEXT_PACK_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "normalized_context_schema"
    / "sample_outputs"
    / "context_pack.json"
)
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent / "sample_outputs" / "json_continuity_check_single_report.md"


def load_context_pack(path: Path = DEFAULT_CONTEXT_PACK_PATH) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_check(new_content: str, context_pack: Dict[str, Any]) -> Dict[str, Any]:
    claims = extract_claims(new_content)
    issues = check_claims_against_context_pack(claims, context_pack)
    return {
        "new_content": new_content,
        "claims": [claim.to_dict() for claim in claims],
        "issues": [issue.to_dict() for issue in issues],
        "decision": decision_from_issues(issues),
        "context_pack_query": context_pack.get("query", ""),
    }


def _append_evidence(lines: List[str], heading: str, items: List[Dict[str, Any]]) -> None:
    lines.extend(["", f"## {heading}", ""])
    if not items:
        lines.append("- None")
        return
    for item in items[:5]:
        lines.append(
            f"- {item.get('source_file', '')} | {item.get('section_title', '')} | "
            f"{item.get('status', '')}: {item.get('excerpt', '')[:220]}"
        )


def format_report(result: Dict[str, Any], context_pack: Dict[str, Any]) -> str:
    lines = [
        "# JSON Continuity Check Report",
        "",
        "## New Content",
        "",
        result["new_content"],
        "",
        "## Extracted Claims",
        "",
    ]
    for claim in result["claims"]:
        lines.append(
            f"- `{claim['claim_id']}` subject={claim['subject']} "
            f"attribute={claim['attribute']} value={claim['value']} "
            f"branch_scope={claim.get('branch_scope') or 'None'} status={claim.get('status') or 'None'}"
        )

    lines.extend(["", "## Issues", ""])
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"### {issue['issue_id']} {issue['issue_type']}")
            lines.append(f"- severity: {issue['severity']}")
            lines.append(f"- explanation: {issue['explanation']}")
            lines.append(f"- suggested_fix: {issue['suggested_fix']}")
            lines.append(f"- source_policy: {issue['source_policy']}")
            lines.append("")
    else:
        lines.append("- None")

    _append_evidence(lines, "Canon Evidence", context_pack.get("canon_context", []))
    _append_evidence(lines, "Draft Reference", context_pack.get("draft_reference", []))
    _append_evidence(lines, "Deprecated Warnings", context_pack.get("deprecated_warnings", []))

    lines.extend(["", "## Missing Evidence", ""])
    missing = context_pack.get("missing_evidence", [])
    if missing:
        for item in missing:
            lines.append(f"- {item.get('description', item)}")
    else:
        lines.append("- None from Context Pack")

    lines.extend(["", "## Decision", "", result["decision"]])
    return "\n".join(lines) + "\n"


def run(
    new_content: str,
    context_pack_path: Path = DEFAULT_CONTEXT_PACK_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    context_pack = load_context_pack(context_pack_path)
    result = run_check(new_content, context_pack)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_report(result, context_pack), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check new content against a JSON Context Pack.")
    parser.add_argument("new_content")
    parser.add_argument("--context-pack", type=Path, default=DEFAULT_CONTEXT_PACK_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    if not args.context_pack.exists():
        print(f"JSON Context Pack not found: {args.context_pack}")
        print("Run experiments/normalized_context_schema/build_json_context_pack.py first.")
        return 1
    output_path = run(args.new_content, args.context_pack, args.output)
    print(f"Wrote JSON continuity report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
