"""Evidence excerpt refinement for Context Pack candidates."""

import re
from typing import Dict, Iterable, List


CHARACTER_IDENTITY_TERMS = [
    "Rin",
    "Nexus-7",
    "仿生人",
    "android",
    "身份",
    "角色设定",
]


def _plan_value(retrieval_plan, key: str, default=None):
    """Read a value from a dataclass-like or dict retrieval plan."""
    if isinstance(retrieval_plan, dict):
        return retrieval_plan.get(key, default)
    return getattr(retrieval_plan, key, default)


def _compact(text: str) -> str:
    """Compact whitespace for CLI-friendly excerpts."""
    return re.sub(r"\s+", " ", text).strip()


def _window(text: str, position: int, length: int = 360) -> str:
    """Return a compact excerpt window around a position."""
    start = max(position - 80, 0)
    end = min(start + length, len(text))
    return _compact(text[start:end])


def _first_match_position(text: str, terms: Iterable[str]) -> int:
    """Return the earliest term position in text, or -1."""
    positions: List[int] = []
    lower_text = text.lower()
    for term in terms:
        position = lower_text.find(term.lower())
        if position >= 0:
            positions.append(position)
    return min(positions) if positions else -1


def refine_evidence_excerpt(candidate: Dict, retrieval_plan) -> str:
    """Return a shorter, more direct excerpt without changing candidate text."""
    text = candidate.get("text", "")
    if not text:
        return candidate.get("excerpt", "")

    metadata = candidate.get("metadata", {})
    intent = _plan_value(retrieval_plan, "intent", "")
    entities = _plan_value(retrieval_plan, "entities", []) or []
    heading = metadata.get("heading", "") or metadata.get("section_title", "")

    if intent == "character_identity":
        terms = list(CHARACTER_IDENTITY_TERMS)
        for entity in entities:
            if entity not in terms:
                terms.insert(0, entity)

        if any(entity and entity.lower() in heading.lower() for entity in entities):
            return _compact(text[:420])

        position = _first_match_position(text, terms)
        if position >= 0:
            return _window(text, position)

    fallback_excerpt = candidate.get("excerpt", "")
    if fallback_excerpt:
        return fallback_excerpt
    return _compact(text[:360])

