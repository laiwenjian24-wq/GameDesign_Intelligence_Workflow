"""Generate a markdown quality report for normalized ingestion blocks."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "knowledge_base" / "import_manifest.json"
EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_BLOCKS_PATH = EXPERIMENT_DIR / "sample_outputs" / "normalized_blocks.jsonl"
DEFAULT_REPORT_PATH = EXPERIMENT_DIR / "sample_outputs" / "docling_ingestion_eval_report.md"
STATUS_VALUES = ("canon", "draft", "deprecated", "inspiration")


def read_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> List[Dict[str, Any]]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def evaluate_blocks(
    blocks: Iterable[Dict[str, Any]],
    manifest_items: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    block_list = list(blocks)
    manifest_list = list(manifest_items)
    manifest_statuses = Counter(item.get("status", "unknown") for item in manifest_list)
    block_statuses = Counter(block.get("status", "unknown") for block in block_list)
    by_source: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for block in block_list:
        by_source[block.get("source_file", "")].append(block)

    required_fields = ("source_file", "status", "section_title", "block_type")
    missing_required = [
        block.get("block_id", "<missing block_id>")
        for block in block_list
        if any(not block.get(field) for field in required_fields)
    ]

    return {
        "block_count": len(block_list),
        "source_count": len(by_source),
        "manifest_statuses": manifest_statuses,
        "block_statuses": block_statuses,
        "missing_required": missing_required,
        "has_heading": any(block.get("heading_path") or block.get("section_title") not in ("", "Metadata only") for block in block_list),
        "has_table": any(block.get("block_type") == "table" for block in block_list),
        "has_image": any(block.get("block_type") in ("image", "caption") for block in block_list),
        "all_have_source": all(bool(block.get("source_file")) for block in block_list) if block_list else False,
        "all_have_status": all(bool(block.get("status")) for block in block_list) if block_list else False,
        "all_have_section": all(bool(block.get("section_title")) for block in block_list) if block_list else False,
        "all_have_type": all(bool(block.get("block_type")) for block in block_list) if block_list else False,
        "represented_statuses": sorted(block_statuses),
    }


def render_report(evaluation: Dict[str, Any]) -> str:
    block_statuses = evaluation["block_statuses"]
    status_lines = [
        f"- `{status}`: {block_statuses.get(status, 0)} normalized block(s)"
        for status in STATUS_VALUES
    ]
    represented_all = all(status in block_statuses for status in STATUS_VALUES)
    suitable_for_context_pack = (
        evaluation["block_count"] > 0
        and evaluation["all_have_source"]
        and evaluation["all_have_status"]
        and evaluation["all_have_section"]
        and evaluation["all_have_type"]
    )

    graph_note = (
        "Suitable as a candidate feed for future source-cited graph extraction."
        if suitable_for_context_pack
        else "Not ready for GraphRAG experiments until required provenance fields are complete."
    )

    lines = [
        "# Docling Ingestion Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Normalized block count: {evaluation['block_count']}",
        f"- Source count: {evaluation['source_count']}",
        f"- Required fields complete: {_yes_no(not evaluation['missing_required'])}",
        f"- Suitable for Context Pack adapter experiment: {_yes_no(suitable_for_context_pack)}",
        f"- GraphRAG readiness note: {graph_note}",
        "",
        "## Status Preservation",
        "",
        *status_lines,
        f"- All four governance statuses represented in normalized outputs: {_yes_no(represented_all)}",
        "",
        "## Field Checks",
        "",
        f"- `source_file` preserved for every block: {_yes_no(evaluation['all_have_source'])}",
        f"- `status` preserved for every block: {_yes_no(evaluation['all_have_status'])}",
        f"- `section_title` preserved for every block: {_yes_no(evaluation['all_have_section'])}",
        f"- `block_type` preserved for every block: {_yes_no(evaluation['all_have_type'])}",
        f"- Heading or section structure detected: {_yes_no(evaluation['has_heading'])}",
        f"- Table block detected: {_yes_no(evaluation['has_table'])}",
        f"- Image/caption block detected: {_yes_no(evaluation['has_image'])}",
        "",
        "## Interpretation",
        "",
        "This report evaluates whether parsed material can preserve v1 narrative governance metadata. A useful parser must keep source, status, section, and block type intact before the material is allowed into Context Pack, index, or future GraphRAG experiments.",
        "",
        "Image and caption support is considered extensible if the normalized schema can represent `image` and `caption` block types, even when the current sample set contains only Markdown metadata.",
    ]

    if evaluation["missing_required"]:
        lines.extend(
            [
                "",
                "## Missing Required Fields",
                "",
                *[f"- `{block_id}`" for block_id in evaluation["missing_required"][:50]],
            ]
        )
    return "\n".join(lines) + "\n"


def run(
    blocks_path: Path = DEFAULT_BLOCKS_PATH,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> Path:
    blocks = read_jsonl(blocks_path)
    manifest_items = read_manifest(manifest_path)
    evaluation = evaluate_blocks(blocks, manifest_items)
    report = render_report(evaluation)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Docling ingestion quality.")
    parser.add_argument("--blocks", type=Path, default=DEFAULT_BLOCKS_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    report_path = run(args.blocks, args.manifest, args.report)
    print(f"Wrote evaluation report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
