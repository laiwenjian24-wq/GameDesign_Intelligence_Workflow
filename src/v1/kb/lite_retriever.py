"""Keyword retriever for the v1 Lite Knowledge Base."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from src.v1.ingestion.status_policy import CANON, DEPRECATED, DRAFT, INSPIRATION, UNKNOWN, get_status_priority
from src.v1.kb.lite_index import LiteKnowledgeBase


STATUS_SCORE = {
    CANON: 5,
    DRAFT: 3,
    DEPRECATED: 2,
    INSPIRATION: 1,
    UNKNOWN: 0,
}


def retrieve_lite_evidence(
    query: str,
    kb: LiteKnowledgeBase,
    top_k: int = 8,
) -> List[Dict[str, Any]]:
    tokens = _query_tokens(query)
    scored = []
    for block in kb.blocks:
        score, reasons = _score_block(tokens, query, block)
        if score <= 0:
            continue
        scored.append((score, block, reasons))
    scored.sort(
        key=lambda item: (
            item[0],
            STATUS_SCORE.get(item[1].get("status", UNKNOWN), 0),
            -abs(len(item[1].get("text", "")) - 500),
        ),
        reverse=True,
    )
    return [_to_evidence(block, score, reasons) for score, block, reasons in scored[:top_k]]


def _query_tokens(query: str) -> List[str]:
    raw = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]{1,4}", query)
    expansions = []
    for token in raw:
        expansions.append(token.lower())
        if token == "右腿":
            expansions.extend(["right leg", "受伤", "伤势"])
        if token == "左腿":
            expansions.extend(["left leg", "受伤", "伤势"])
        if token.lower() == "rin":
            expansions.extend(["nexus", "仿生人", "身份"])
        if token.lower() == "mouse":
            expansions.extend(["鼠", "伤势"])
        if token.lower() == "mombasa":
            expansions.extend(["安全屋", "safehouse"])
    return [token for token in expansions if token]


def _score_block(tokens: List[str], query: str, block: Dict[str, Any]) -> tuple[int, List[str]]:
    haystack = " ".join(
        [
            block.get("source_file", ""),
            block.get("section_title", ""),
            " ".join(block.get("heading_path", [])),
            block.get("text", ""),
            " ".join(str(tag) for tag in block.get("metadata", {}).get("tags", [])),
            block.get("metadata", {}).get("asset_type", ""),
        ]
    ).lower()
    score = 0
    reasons: List[str] = []
    for token in tokens:
        if token.lower() in haystack:
            score += 2 if len(token) > 1 else 1
            reasons.append(f"matched:{token}")
    status = block.get("status", UNKNOWN)
    score += STATUS_SCORE.get(status, 0)
    if "Branch B".lower() in query.lower() and ("branch_b" in haystack or "branch b" in haystack):
        score += 3
        reasons.append("matched:branch_scope")
    if block.get("block_type") == "table_or_code":
        score += 1
        reasons.append("table_or_code")
    if len(block.get("text", "")) > 2000:
        score -= 1
    return score, reasons


def _to_evidence(block: Dict[str, Any], score: int, reasons: List[str]) -> Dict[str, Any]:
    text = block.get("text", "")
    excerpt = " ".join(text.split())[:500]
    return {
        "evidence_id": block.get("block_id", ""),
        "source_file": block.get("source_file", ""),
        "original_path": block.get("original_path", ""),
        "status": block.get("status", UNKNOWN),
        "status_priority": get_status_priority(block.get("status", UNKNOWN)),
        "section_title": block.get("section_title", ""),
        "heading_path": block.get("heading_path", []),
        "block_type": block.get("block_type", "unknown"),
        "text": text,
        "excerpt": excerpt,
        "source_ref": f"{block.get('source_file', '')}::{block.get('section_title', '')}::{block.get('block_id', '')}",
        "reason_used": ", ".join(reasons[:8]),
        "score": score,
        "metadata": block.get("metadata", {}),
    }
