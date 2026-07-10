"""Build an experimental Context Pack from normalized blocks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

try:
    from .evidence_adapter import adapt_blocks_to_evidence, group_evidence_by_status
    from .normalized_block_loader import DEFAULT_BLOCKS_PATH, NormalizedBlocksMissingError, load_normalized_blocks
except ImportError:  # pragma: no cover - supports direct script execution
    from evidence_adapter import adapt_blocks_to_evidence, group_evidence_by_status
    from normalized_block_loader import DEFAULT_BLOCKS_PATH, NormalizedBlocksMissingError, load_normalized_blocks


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = EXPERIMENT_DIR / "sample_outputs" / "normalized_context_pack.md"

QUERY_SYNONYMS = {
    "身份": ["身份", "职业", "背景", "Nexus", "仿生人"],
    "实验对象": ["实验对象", "实验", "脑梯", "培养", "Nexus"],
    "受伤": ["受伤", "负伤", "擦伤", "腿", "右腿", "左腿", "伤口"],
    "第二基地": ["第二基地", "Second Foundation", "反抗", "组织"],
    "旧版": ["旧版", "旧稿", "Deprecated", "deprecated", "覆盖", "Canon"],
    "canon": ["Canon", "canon", "当前", "事实", "覆盖"],
}


def tokenize_query(query: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]{1,4}", query)
    expanded: List[str] = []
    for token in tokens:
        expanded.append(token)
        expanded.extend(QUERY_SYNONYMS.get(token, []))
    for key, synonyms in QUERY_SYNONYMS.items():
        if key in query:
            expanded.extend(synonyms)
    return [token.lower() for token in expanded if token.strip()]


def score_evidence(query: str, evidence: Dict[str, Any]) -> int:
    haystack = " ".join(
        [
            evidence.get("source_file", ""),
            evidence.get("section_title", ""),
            " ".join(str(part) for part in evidence.get("heading_path", [])),
            evidence.get("text", ""),
            " ".join(str(tag) for tag in evidence.get("metadata", {}).get("tags", [])),
            evidence.get("metadata", {}).get("asset_type", ""),
        ]
    ).lower()
    score = 0
    for token in tokenize_query(query):
        if token in haystack:
            score += 1
    if evidence.get("block_type") == "table":
        score += 1
    return score


def select_evidence(
    query: str,
    evidence_items: Iterable[Dict[str, Any]],
    per_group_limit: int = 5,
) -> Tuple[Dict[str, List[Dict[str, Any]]], List[str]]:
    scored = [
        (score_evidence(query, item), item)
        for item in evidence_items
    ]
    relevant = [item for score, item in scored if score > 0]
    grouped = group_evidence_by_status(relevant)
    selected: Dict[str, List[Dict[str, Any]]] = {}
    for group_name, items in grouped.items():
        selected[group_name] = sorted(
            items,
            key=lambda item: score_evidence(query, item),
            reverse=True,
        )[:per_group_limit]

    missing_evidence: List[str] = []
    if not selected.get("canon_context"):
        missing_evidence.append(
            "No canon evidence found in normalized blocks for this query. Do not make current-truth decisions without human review."
        )
    return selected, missing_evidence


def build_context_pack(
    query: str,
    blocks_path: Path = DEFAULT_BLOCKS_PATH,
    per_group_limit: int = 5,
) -> Dict[str, Any]:
    blocks = load_normalized_blocks(blocks_path)
    evidence = adapt_blocks_to_evidence(blocks)
    selected, missing_evidence = select_evidence(query, evidence, per_group_limit=per_group_limit)
    return {
        "query": query,
        "groups": selected,
        "missing_evidence": missing_evidence,
        "source_summary": _source_summary(selected),
    }


def _source_summary(groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    summary: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for group_name, items in groups.items():
        for item in items:
            key = (item.get("source_file", ""), item.get("status", "unknown"))
            summary.setdefault(
                key,
                {
                    "source_file": item.get("source_file", ""),
                    "status": item.get("status", "unknown"),
                    "groups": set(),
                    "sections": set(),
                },
            )
            summary[key]["groups"].add(group_name)
            summary[key]["sections"].add(item.get("section_title", ""))
    rendered = []
    for item in summary.values():
        rendered.append(
            {
                "source_file": item["source_file"],
                "status": item["status"],
                "groups": sorted(item["groups"]),
                "sections": sorted(section for section in item["sections"] if section),
            }
        )
    return sorted(rendered, key=lambda item: (item["status"], item["source_file"]))


def _append_evidence_section(lines: List[str], heading: str, items: List[Dict[str, Any]]) -> None:
    lines.extend(["", f"## {heading}", ""])
    if not items:
        lines.append("- None")
        return
    for item in items:
        lines.append(f"### {item.get('source_file', '')}")
        lines.append(f"- section_title: {item.get('section_title', '')}")
        lines.append(f"- status: {item.get('status', '')}")
        lines.append(f"- block_type: {item.get('block_type', '')}")
        lines.append(f"- source_ref: {item.get('source_ref', '')}")
        lines.append(f"- reason_used: {item.get('reason_used', '')}")
        lines.append("")
        lines.append(f"> {item.get('excerpt', '')}")
        lines.append("")


def format_context_pack_markdown(context_pack: Dict[str, Any]) -> str:
    groups = context_pack.get("groups", {})
    lines = [
        "# Normalized Context Pack",
        "",
        "## Query",
        "",
        context_pack.get("query", ""),
    ]
    _append_evidence_section(lines, "Canon Context", groups.get("canon_context", []))
    _append_evidence_section(lines, "Draft Reference", groups.get("draft_reference", []))
    _append_evidence_section(lines, "Deprecated Warnings", groups.get("deprecated_warnings", []))
    _append_evidence_section(lines, "Inspiration Reference", groups.get("inspiration_reference", []))

    lines.extend(["", "## Missing Evidence", ""])
    missing = context_pack.get("missing_evidence", [])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- None")

    lines.extend(["", "## Source Summary", ""])
    summary = context_pack.get("source_summary", [])
    if not summary:
        lines.append("- None")
    for source in summary:
        sections = "; ".join(source.get("sections", []))
        groups = ", ".join(source.get("groups", []))
        lines.append(
            f"- {source.get('source_file', '')} "
            f"[{source.get('status', '')}; {groups}] sections: {sections}"
        )
    return "\n".join(lines).rstrip() + "\n"


def run(
    query: str,
    blocks_path: Path = DEFAULT_BLOCKS_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    context_pack = build_context_pack(query, blocks_path=blocks_path)
    markdown = format_context_pack_markdown(context_pack)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a normalized-block Context Pack.")
    parser.add_argument("query")
    parser.add_argument("--blocks", type=Path, default=DEFAULT_BLOCKS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    try:
        output_path = run(args.query, blocks_path=args.blocks, output_path=args.output)
    except NormalizedBlocksMissingError as exc:
        print(str(exc))
        return 1
    print(f"Wrote normalized context pack: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
