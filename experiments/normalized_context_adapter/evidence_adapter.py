"""Adapt normalized document blocks into Context Pack-style evidence items."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List


STATUS_PRIORITY = {
    "canon": "highest",
    "draft": "reference only",
    "deprecated": "warning only",
    "inspiration": "inspiration only",
    "unknown": "review required",
}

STATUS_GROUPS = {
    "canon": "canon_context",
    "draft": "draft_reference",
    "deprecated": "deprecated_warnings",
    "inspiration": "inspiration_reference",
    "unknown": "unknown_review",
}


def _excerpt(text: str, max_chars: int = 360) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3].rstrip() + "..."


def _source_ref(block: Dict[str, Any]) -> str:
    source = block.get("source_file") or Path(block.get("original_path", "")).name
    section = block.get("section_title") or "Unknown section"
    block_id = block.get("block_id", "")
    return f"{source} :: {section} :: {block_id}"


def adapt_block_to_evidence(block: Dict[str, Any]) -> Dict[str, Any]:
    status = str(block.get("status", "unknown") or "unknown").lower()
    if status not in STATUS_PRIORITY:
        status = "unknown"
    metadata = dict(block.get("metadata", {}) or {})
    reason_used = {
        "canon": "Canon evidence: usable as current truth if relevant.",
        "draft": "Draft reference only: cannot override Canon.",
        "deprecated": "Deprecated warning only: historical conflict source, not current truth.",
        "inspiration": "Inspiration reference only: not factual evidence.",
        "unknown": "Unknown status: review required before use.",
    }[status]

    return {
        "source_file": block.get("source_file", ""),
        "original_path": block.get("original_path", ""),
        "status": status,
        "section_title": block.get("section_title", ""),
        "heading_path": block.get("heading_path", []),
        "block_type": block.get("block_type", "unknown"),
        "text": block.get("text", ""),
        "excerpt": _excerpt(block.get("text", "")),
        "metadata": metadata,
        "source_ref": _source_ref(block),
        "status_priority": STATUS_PRIORITY[status],
        "reason_used": reason_used,
    }


def adapt_blocks_to_evidence(blocks: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [adapt_block_to_evidence(block) for block in blocks]


def group_evidence_by_status(evidence_items: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped = {group: [] for group in STATUS_GROUPS.values()}
    for item in evidence_items:
        status = item.get("status", "unknown")
        group_name = STATUS_GROUPS.get(status, "unknown_review")
        grouped.setdefault(group_name, []).append(item)
    return grouped
