"""Keyword retrieval for the first search MVP."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from src.retrieval.status_priority import build_reason_used, get_status_priority


def _tokenize(query: str) -> List[str]:
    """Tokenize English words and CJK character groups conservatively."""
    tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+", query.lower())
    return [token for token in tokens if token.strip()]


def _load_index(index_dir: Path) -> List[Dict]:
    """Load the local keyword index from disk."""
    index_path = index_dir / "keyword_index.json"
    if not index_path.exists():
        return []
    return json.loads(index_path.read_text(encoding="utf-8"))


def _score_record(record: Dict, tokens: List[str]) -> int:
    """Score a record using simple weighted keyword occurrence counts."""
    metadata = record.get("metadata", {})
    searchable_text = record.get("searchable_text", "")

    score = 0
    filename = metadata.get("filename", "").lower()
    summary = metadata.get("summary", "").lower()

    for token in tokens:
        if token in filename:
            score += 5
        if token in summary:
            score += 3
        score += searchable_text.count(token)

    return score


def _build_excerpt(text: str, tokens: List[str], max_length: int = 220) -> str:
    """Return a short excerpt around the first matching query token."""
    if not text:
        return ""

    lower_text = text.lower()
    match_positions = [
        lower_text.find(token) for token in tokens if lower_text.find(token) >= 0
    ]

    if match_positions:
        start = max(min(match_positions) - 60, 0)
    else:
        start = 0

    excerpt = text[start : start + max_length].strip()
    excerpt = re.sub(r"\s+", " ", excerpt)
    if start > 0:
        excerpt = f"...{excerpt}"
    if start + max_length < len(text):
        excerpt = f"{excerpt}..."
    return excerpt


def query_knowledge_base(
    question: str,
    index_dir: Path,
    filters: Optional[Dict] = None,
    top_k: int = 5,
) -> List[Dict]:
    """Query the local keyword index and return the most relevant records."""
    tokens = _tokenize(question)
    if not tokens:
        return []

    results = []
    for record in _load_index(index_dir):
        metadata = record.get("metadata", {})

        if filters:
            should_skip = any(
                metadata.get(key) != value for key, value in filters.items()
            )
            if should_skip:
                continue

        score = _score_record(record, tokens)
        if score <= 0:
            continue

        status = metadata.get("status", "unknown")
        excerpt = _build_excerpt(record.get("text", ""), tokens)
        results.append(
            {
                "score": score,
                "status_priority": get_status_priority(status),
                "filename": metadata.get("filename", ""),
                "source_file": metadata.get("filename", ""),
                "status": status,
                "summary": metadata.get("summary", ""),
                "excerpt": excerpt,
                "relevant_excerpt": excerpt,
                "file_path": metadata.get("file_path", ""),
                "reason_used": build_reason_used(status, score),
            }
        )

    results.sort(
        key=lambda item: (
            -item["score"],
            -item["status_priority"],
            item["filename"],
        )
    )
    return results[: max(3, min(top_k, 5))]
