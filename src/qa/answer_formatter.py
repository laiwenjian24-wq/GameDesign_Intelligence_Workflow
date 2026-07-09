"""Markdown formatter for Narrative QA answer reports."""

from typing import Dict, List


def _append_list(lines: List[str], items: List[str]) -> None:
    """Append a Markdown list or a None marker."""
    if not items:
        lines.append("- None")
        return
    for item in items:
        lines.append(f"- {item}")


def format_qa_report_markdown(report: Dict) -> str:
    """Format a Narrative QA report as Markdown."""
    answer = report.get("answer", {})
    lines = [
        "# Narrative QA Answer",
        "",
        "## Question",
        report.get("question", ""),
        "",
        "## Mode",
        f"- {report.get('mode', '')}",
        "",
        "## Provider",
        f"- {report.get('provider', 'fake')}",
        "",
        "## Answer",
        answer.get("answer", ""),
        "",
        "## Confidence",
        f"- {answer.get('confidence', 'low')}",
        "",
        "## Canon Sources",
    ]
    _append_list(lines, answer.get("canon_sources", []))

    lines.extend(["", "## Draft Notes"])
    _append_list(lines, answer.get("draft_notes", []))

    lines.extend(["", "## Deprecated Warnings"])
    _append_list(lines, answer.get("deprecated_warnings", []))

    lines.extend(["", "## Missing Evidence"])
    _append_list(lines, answer.get("missing_evidence", []))

    lines.extend(["", "## Limitations"])
    _append_list(lines, answer.get("limitations", []))

    return "\n".join(lines)
