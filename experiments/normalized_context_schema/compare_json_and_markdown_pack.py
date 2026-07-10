"""Compare JSON and Markdown Context Pack representations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON_PATH = PROJECT_ROOT / "experiments" / "normalized_context_schema" / "sample_outputs" / "context_pack.json"
DEFAULT_MARKDOWN_PATH = PROJECT_ROOT / "experiments" / "normalized_context_adapter" / "sample_outputs" / "normalized_context_pack.md"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "experiments" / "normalized_context_schema" / "sample_outputs" / "json_vs_markdown_context_pack_report.md"


def compare(json_path: Path = DEFAULT_JSON_PATH, markdown_path: Path = DEFAULT_MARKDOWN_PATH) -> Dict[str, Any]:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
    diagnostics = payload.get("diagnostics", {})
    return {
        "json_exists": json_path.exists(),
        "markdown_exists": markdown_path.exists(),
        "json_query": payload.get("query", ""),
        "json_has_diagnostics": bool(diagnostics),
        "json_has_missing_evidence": "missing_evidence" in payload,
        "json_has_grouped_lists": all(
            isinstance(payload.get(field), list)
            for field in (
                "canon_context",
                "draft_reference",
                "deprecated_warnings",
                "inspiration_reference",
            )
        ),
        "markdown_has_headings": "# Normalized Context Pack" in markdown and "## Canon Context" in markdown,
        "markdown_line_count": len(markdown.splitlines()) if markdown else 0,
        "json_evidence_counts": diagnostics.get("evidence_count_by_status", {}),
    }


def render_report(comparison: Dict[str, Any]) -> str:
    lines = [
        "# JSON vs Markdown Context Pack Report",
        "",
        "## Summary",
        "",
        f"- JSON pack exists: {'yes' if comparison['json_exists'] else 'no'}",
        f"- Markdown pack exists: {'yes' if comparison['markdown_exists'] else 'no'}",
        f"- JSON has diagnostics: {'yes' if comparison['json_has_diagnostics'] else 'no'}",
        f"- JSON has grouped evidence lists: {'yes' if comparison['json_has_grouped_lists'] else 'no'}",
        f"- Markdown has human-readable headings: {'yes' if comparison['markdown_has_headings'] else 'no'}",
        f"- Markdown line count: {comparison['markdown_line_count']}",
        f"- JSON evidence counts: {comparison['json_evidence_counts']}",
        "",
        "## Interpretation",
        "",
        "JSON is better for future `chat` and `check-continuity` because it can be validated before use, passed through deterministic workflow code, and inspected by tests for status separation.",
        "",
        "Markdown is better for human review, debug output, handoff notes, and portfolio screenshots because it is readable without tooling.",
        "",
        "The recommended v1 direction is to keep JSON as the source-of-truth Context Pack object and render Markdown from it for reports.",
    ]
    return "\n".join(lines) + "\n"


def run(
    json_path: Path = DEFAULT_JSON_PATH,
    markdown_path: Path = DEFAULT_MARKDOWN_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> Path:
    comparison = compare(json_path=json_path, markdown_path=markdown_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(comparison), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare JSON and Markdown Context Pack outputs.")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    report_path = run(args.json, args.markdown, args.report)
    print(f"Wrote JSON vs Markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
