"""Status priority and source-use rules for retrieval and continuity checks.

The resolver is intentionally small and deterministic. It does not decide
truth by itself; it explains how each source status may be used.
"""

from typing import Dict, List


STATUS_PRIORITY = {
    "canon": 100,
    "draft": 70,
    "pattern": 60,
    "inspiration": 40,
    "deprecated": 10,
    "unknown": 0,
}


STATUS_USAGE_RULES = {
    "canon": "Authoritative evidence. Use as the primary continuity basis.",
    "draft": "Reference only. Useful for intent, but cannot override Canon.",
    "pattern": "Structural reference only. Do not treat as story fact.",
    "inspiration": "Inspiration only. Do not treat as project fact.",
    "deprecated": "Historical / conflict evidence only. Do not use as current truth.",
    "unknown": "Unverified source. Requires human review before use.",
}


def normalize_status(status: str) -> str:
    """Normalize unknown or mixed-case status values."""
    normalized = (status or "unknown").strip().lower()
    if normalized not in STATUS_PRIORITY:
        return "unknown"
    return normalized


def get_status_priority(status: str) -> int:
    """Return the deterministic priority for a status."""
    return STATUS_PRIORITY[normalize_status(status)]


def get_usage_rule(status: str) -> str:
    """Return the source-use rule for a status."""
    return STATUS_USAGE_RULES[normalize_status(status)]


def build_reason_used(status: str, score: int) -> str:
    """Explain why a retrieval result is included."""
    normalized = normalize_status(status)
    priority = get_status_priority(normalized)
    rule = get_usage_rule(normalized)
    return (
        f"keyword_score={score}; status={normalized}; "
        f"status_priority={priority}; rule={rule}"
    )


def group_sources_by_status(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Group cited results into the known status buckets."""
    grouped = {status: [] for status in STATUS_PRIORITY}
    for result in results:
        status = normalize_status(result.get("status", "unknown"))
        grouped[status].append(result)
    return grouped
