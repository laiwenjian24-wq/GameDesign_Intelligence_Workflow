"""Metadata schema placeholders.

These names reflect the first Narrative Workflow ingestion design:
- canon
- draft
- inspiration
- deprecated
- pattern
- unknown
"""

from enum import Enum


class AssetClass(str, Enum):
    """Allowed narrative asset classes."""

    CANON = "canon"
    DRAFT = "draft"
    INSPIRATION = "inspiration"
    DEPRECATED = "deprecated"
    PATTERN = "pattern"
    UNKNOWN = "unknown"


class DetectedDomain(str, Enum):
    """Allowed first-pass narrative asset domains."""

    NARRATIVE = "narrative"
    SYSTEM = "system"
    VISUAL = "visual"
    UNKNOWN = "unknown"


def build_empty_metadata() -> dict:
    """Return an empty metadata shape for future implementation."""
    return {
        "asset_id": None,
        "filename": None,
        "file_path": None,
        "file_type": None,
        "detected_domain": DetectedDomain.UNKNOWN.value,
        "status": AssetClass.UNKNOWN.value,
        "project": "unknown",
        "related_characters": [],
        "related_locations": [],
        "related_branches": [],
        "tags": [],
        "summary": "",
    }
