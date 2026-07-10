"""Validate candidate JSON Context Packs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_CONTEXT_PACK_PATH = EXPERIMENT_DIR / "sample_outputs" / "context_pack.json"
DEFAULT_REPORT_PATH = EXPERIMENT_DIR / "sample_outputs" / "context_pack_validation_report.md"

REQUIRED_TOP_LEVEL = [
    "query",
    "canon_context",
    "draft_reference",
    "deprecated_warnings",
    "inspiration_reference",
    "missing_evidence",
    "source_summary",
    "diagnostics",
    "metadata",
]
REQUIRED_EVIDENCE_FIELDS = [
    "evidence_id",
    "source_file",
    "original_path",
    "status",
    "status_priority",
    "section_title",
    "heading_path",
    "block_type",
    "excerpt",
    "source_ref",
    "reason_used",
    "metadata",
]
REQUIRED_DIAGNOSTICS = [
    "source_count",
    "evidence_count_by_status",
    "canon_count",
    "draft_count",
    "deprecated_count",
    "inspiration_count",
    "has_canon_evidence",
    "warnings",
]
GROUP_EXPECTED_STATUS = {
    "canon_context": "canon",
    "draft_reference": "draft",
    "deprecated_warnings": "deprecated",
    "inspiration_reference": "inspiration",
}


def validate_context_pack(payload: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    for field in REQUIRED_TOP_LEVEL:
        if field not in payload:
            errors.append(f"Missing top-level field: {field}")

    for group_name, expected_status in GROUP_EXPECTED_STATUS.items():
        for index, item in enumerate(payload.get(group_name, []), start=1):
            for field in REQUIRED_EVIDENCE_FIELDS:
                if field not in item:
                    errors.append(f"{group_name}[{index}] missing field: {field}")
            for field in ("source_file", "status", "section_title"):
                if not item.get(field):
                    errors.append(f"{group_name}[{index}] has empty required field: {field}")
            if item.get("status") != expected_status:
                errors.append(
                    f"{group_name}[{index}] has status {item.get('status')} but expected {expected_status}"
                )

    diagnostics = payload.get("diagnostics", {})
    for field in REQUIRED_DIAGNOSTICS:
        if field not in diagnostics:
            errors.append(f"diagnostics missing field: {field}")

    if payload.get("canon_context"):
        bad_canon = [
            item.get("evidence_id", "<unknown>")
            for item in payload.get("canon_context", [])
            if item.get("status") != "canon"
        ]
        for evidence_id in bad_canon:
            errors.append(f"Non-canon evidence in canon_context: {evidence_id}")
    elif not payload.get("missing_evidence"):
        errors.append("missing_evidence must be non-empty when canon_context is empty")

    expected_counts = {
        "canon": len(payload.get("canon_context", [])),
        "draft": len(payload.get("draft_reference", [])),
        "deprecated": len(payload.get("deprecated_warnings", [])),
        "inspiration": len(payload.get("inspiration_reference", [])),
    }
    actual_counts = diagnostics.get("evidence_count_by_status", {})
    for status, count in expected_counts.items():
        if actual_counts.get(status) != count:
            errors.append(
                f"diagnostics.evidence_count_by_status[{status}] is {actual_counts.get(status)} but expected {count}"
            )

    if diagnostics.get("has_canon_evidence") != bool(payload.get("canon_context")):
        errors.append("diagnostics.has_canon_evidence does not match canon_context")

    for warning in diagnostics.get("warnings", []):
        warnings.append(str(warning))

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "expected_counts": expected_counts,
    }


def render_report(validation: Dict[str, Any]) -> str:
    lines = [
        "# Context Pack Validation Report",
        "",
        f"- valid: {'yes' if validation['valid'] else 'no'}",
        f"- errors: {len(validation['errors'])}",
        f"- warnings: {len(validation['warnings'])}",
        f"- evidence counts: {validation['expected_counts']}",
        "",
        "## Errors",
        "",
    ]
    if validation["errors"]:
        lines.extend(f"- {error}" for error in validation["errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if validation["warnings"]:
        lines.extend(f"- {warning}" for warning in validation["warnings"])
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def run(
    context_pack_path: Path = DEFAULT_CONTEXT_PACK_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> Path:
    payload = json.loads(context_pack_path.read_text(encoding="utf-8"))
    validation = validate_context_pack(payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(validation), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate candidate JSON Context Pack.")
    parser.add_argument("--context-pack", type=Path, default=DEFAULT_CONTEXT_PACK_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    report_path = run(args.context_pack, args.report)
    print(f"Wrote validation report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
