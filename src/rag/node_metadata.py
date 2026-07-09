"""Metadata normalization for LlamaIndex documents and nodes."""

from pathlib import Path
from typing import Dict


REQUIRED_METADATA_FIELDS = [
    "source_file",
    "status",
    "asset_type",
    "tags",
    "reason",
    "expected_usage",
    "metadata_source",
]


def metadata_from_manifest_item(item: Dict, metadata_source: str) -> Dict:
    """Build stable node metadata from one import manifest item."""
    file_path = item.get("file_path", "")
    source_file = item.get("source_file") or Path(file_path).name

    return {
        "source_file": source_file,
        "status": item.get("status", "unknown"),
        "asset_type": item.get("asset_type", "unknown"),
        "tags": item.get("tags", []),
        "reason": item.get("reason", ""),
        "expected_usage": item.get("expected_usage", ""),
        "metadata_source": metadata_source,
        "file_path": file_path,
    }


def ensure_node_metadata(metadata: Dict) -> Dict:
    """Return metadata with all fields required by the Context Pack path."""
    normalized = dict(metadata or {})
    for field in REQUIRED_METADATA_FIELDS:
        if field == "tags":
            normalized.setdefault(field, [])
        else:
            normalized.setdefault(field, "")
    normalized.setdefault("file_path", "")
    return normalized

