"""Metadata extraction placeholder."""

import re
from pathlib import Path
from typing import List, Tuple


CHARACTER_PATTERNS = (
    r"角色[:：]\s*([^\n]+)",
    r"character[s]?[:：]\s*([^\n]+)",
)

LOCATION_PATTERNS = (
    r"地点[:：]\s*([^\n]+)",
    r"场所[:：]\s*([^\n]+)",
    r"location[s]?[:：]\s*([^\n]+)",
)

BRANCH_PATTERNS = (
    r"分支[:：]\s*([^\n]+)",
    r"路线[:：]\s*([^\n]+)",
    r"branch(?:es)?[:：]\s*([^\n]+)",
)

TAG_PATTERNS = (
    r"标签[:：]\s*([^\n]+)",
    r"tags?[:：]\s*([^\n]+)",
)


def _split_values(raw: str) -> List[str]:
    """Split comma-like metadata values while preserving Chinese text."""
    values = re.split(r"[,，、;/；|]", raw)
    return sorted({value.strip() for value in values if value.strip()})


def _extract_pattern_values(text: str, patterns: Tuple[str, ...]) -> List[str]:
    """Extract simple frontmatter-like or note-like metadata values."""
    results: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            results.update(_split_values(match.group(1)))
    return sorted(results)


def _build_summary(text: str, max_length: int = 180) -> str:
    """Build a simple extractive summary from the first meaningful line."""
    for line in text.splitlines():
        cleaned = line.strip().lstrip("#").strip()
        if cleaned:
            if len(cleaned) <= max_length:
                return cleaned
            return f"{cleaned[:max_length].rstrip()}..."
    return ""


def extract_metadata(text: str, source_metadata: dict) -> dict:
    """Extract simple metadata from source text without calling an LLM.

    The first version uses explicit labels in notes, path information, and the
    first meaningful line as a summary draft.
    """
    source_path = Path(source_metadata.get("source_path", ""))
    path_tags = [
        part
        for part in source_path.parts
        if part.lower() not in {"knowledge_base", "raw_assets"}
        and part != source_path.name
    ]

    explicit_tags = _extract_pattern_values(text, TAG_PATTERNS)

    return {
        "related_characters": _extract_pattern_values(text, CHARACTER_PATTERNS),
        "related_locations": _extract_pattern_values(text, LOCATION_PATTERNS),
        "related_branches": _extract_pattern_values(text, BRANCH_PATTERNS),
        "tags": sorted(set(path_tags + explicit_tags)),
        "summary": _build_summary(text),
    }
