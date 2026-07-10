"""Canon-aware source status policy for v1."""

from typing import Dict


CANON = "canon"
DRAFT = "draft"
DEPRECATED = "deprecated"
INSPIRATION = "inspiration"
UNKNOWN = "unknown"

VALID_STATUSES = {CANON, DRAFT, DEPRECATED, INSPIRATION, UNKNOWN}

STATUS_PRIORITIES: Dict[str, str] = {
    CANON: "highest",
    DRAFT: "reference only",
    DEPRECATED: "warning only",
    INSPIRATION: "inspiration only",
    UNKNOWN: "review required",
}


def normalize_status(status: str) -> str:
    normalized = str(status or UNKNOWN).strip().lower()
    return normalized if normalized in VALID_STATUSES else UNKNOWN


def get_status_priority(status: str) -> str:
    return STATUS_PRIORITIES[normalize_status(status)]


def is_current_truth(status: str) -> bool:
    return normalize_status(status) == CANON


def is_reference_only(status: str) -> bool:
    return normalize_status(status) == DRAFT


def is_warning_only(status: str) -> bool:
    return normalize_status(status) == DEPRECATED


def can_enter_canon_context(status: str) -> bool:
    return normalize_status(status) == CANON
