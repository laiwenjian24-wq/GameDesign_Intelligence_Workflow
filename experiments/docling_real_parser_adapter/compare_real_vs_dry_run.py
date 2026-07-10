"""Compare real Docling normalized blocks against dry-run normalized blocks."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DRY_RUN_PATH = PROJECT_ROOT / "experiments" / "docling_ingestion_eval" / "sample_outputs" / "normalized_blocks.jsonl"
DEFAULT_REAL_PATH = PROJECT_ROOT / "experiments" / "docling_real_parser_adapter" / "sample_outputs" / "real_docling_normalized_blocks.jsonl"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "experiments" / "docling_real_parser_adapter" / "sample_outputs" / "real_vs_dry_run_report.md"


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _has_chinese(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text or "")


def summarize(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = Counter(block.get("status", "unknown") for block in blocks)
    sources = {block.get("source_file", "") for block in blocks if block.get("source_file")}
    heading_count = sum(1 for block in blocks if block.get("heading_path"))
    table_count = sum(1 for block in blocks if block.get("block_type") == "table")
    page_count = sum(1 for block in blocks if block.get("page_number") is not None)
    required_ok = all(
        block.get("source_file") and block.get("status") and block.get("section_title")
        for block in blocks
    ) if blocks else False
    chinese_count = sum(1 for block in blocks if _has_chinese(block.get("text", "")))
    return {
        "block_count": len(blocks),
        "source_count": len(sources),
        "statuses": dict(statuses),
        "heading_count": heading_count,
        "table_count": table_count,
        "page_number_count": page_count,
        "required_fields_ok": required_ok,
        "chinese_text_block_count": chinese_count,
    }


def render_report(dry_summary: Dict[str, Any], real_summary: Dict[str, Any]) -> str:
    suitable = real_summary["block_count"] > 0 and real_summary["required_fields_ok"]
    lines = [
        "# Real Docling vs Dry-run Ingestion Report",
        "",
        "## Summary",
        "",
        "| Metric | Dry-run | Real Docling |",
        "|---|---:|---:|",
        f"| block count | {dry_summary['block_count']} | {real_summary['block_count']} |",
        f"| source count | {dry_summary['source_count']} | {real_summary['source_count']} |",
        f"| heading preservation | {dry_summary['heading_count']} | {real_summary['heading_count']} |",
        f"| table preservation | {dry_summary['table_count']} | {real_summary['table_count']} |",
        f"| page number preservation | {dry_summary['page_number_count']} | {real_summary['page_number_count']} |",
        f"| Chinese text blocks | {dry_summary['chinese_text_block_count']} | {real_summary['chinese_text_block_count']} |",
        "",
        "## Status Preservation",
        "",
        f"- dry-run statuses: {dry_summary['statuses']}",
        f"- real Docling statuses: {real_summary['statuses']}",
        "",
        "## Source / Section Preservation",
        "",
        f"- dry-run required fields ok: {'yes' if dry_summary['required_fields_ok'] else 'no'}",
        f"- real Docling required fields ok: {'yes' if real_summary['required_fields_ok'] else 'no'}",
        "",
        "## V1 Context Pack Suitability",
        "",
        (
            "- Real Docling output is suitable as a v1 Context Pack candidate input."
            if suitable
            else "- Real Docling output is not yet suitable or was not generated. Install Docling and parse available files before evaluating suitability."
        ),
    ]
    return "\n".join(lines) + "\n"


def run(
    dry_run_path: Path = DEFAULT_DRY_RUN_PATH,
    real_path: Path = DEFAULT_REAL_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> Path:
    dry_blocks = read_jsonl(dry_run_path)
    real_blocks = read_jsonl(real_path)
    report = render_report(summarize(dry_blocks), summarize(real_blocks))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare real Docling output with dry-run normalized blocks.")
    parser.add_argument("--dry-run", type=Path, default=DEFAULT_DRY_RUN_PATH)
    parser.add_argument("--real", type=Path, default=DEFAULT_REAL_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    report_path = run(args.dry_run, args.real, args.report)
    print(f"Wrote real vs dry-run report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
