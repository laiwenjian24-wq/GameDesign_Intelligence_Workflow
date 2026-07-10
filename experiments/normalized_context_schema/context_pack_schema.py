"""Candidate JSON schema for normalized v1 Context Packs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


VALID_STATUSES = {"canon", "draft", "deprecated", "inspiration", "unknown"}


@dataclass
class EvidenceItem:
    evidence_id: str
    source_file: str
    original_path: str
    status: str
    status_priority: str
    section_title: str
    heading_path: List[str]
    block_type: str
    excerpt: str
    source_ref: str
    reason_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MissingEvidence:
    description: str
    severity: str
    related_entities: List[str] = field(default_factory=list)
    suggested_next_step: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Diagnostics:
    source_count: int
    evidence_count_by_status: Dict[str, int]
    canon_count: int
    draft_count: int
    deprecated_count: int
    inspiration_count: int
    has_canon_evidence: bool
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextPack:
    query: str
    canon_context: List[EvidenceItem] = field(default_factory=list)
    draft_reference: List[EvidenceItem] = field(default_factory=list)
    deprecated_warnings: List[EvidenceItem] = field(default_factory=list)
    inspiration_reference: List[EvidenceItem] = field(default_factory=list)
    missing_evidence: List[MissingEvidence] = field(default_factory=list)
    source_summary: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: Optional[Diagnostics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    task_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return payload


def evidence_from_adapter_item(item: Dict[str, Any], evidence_id: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_file=item.get("source_file", ""),
        original_path=item.get("original_path", ""),
        status=item.get("status", "unknown"),
        status_priority=item.get("status_priority", ""),
        section_title=item.get("section_title", ""),
        heading_path=list(item.get("heading_path", [])),
        block_type=item.get("block_type", "unknown"),
        excerpt=item.get("excerpt", ""),
        text=item.get("text"),
        source_ref=item.get("source_ref", ""),
        reason_used=item.get("reason_used", ""),
        metadata=dict(item.get("metadata", {}) or {}),
    )


def build_diagnostics(
    canon_context: List[EvidenceItem],
    draft_reference: List[EvidenceItem],
    deprecated_warnings: List[EvidenceItem],
    inspiration_reference: List[EvidenceItem],
) -> Diagnostics:
    counts = {
        "canon": len(canon_context),
        "draft": len(draft_reference),
        "deprecated": len(deprecated_warnings),
        "inspiration": len(inspiration_reference),
    }
    sources = {
        item.source_file
        for group in (canon_context, draft_reference, deprecated_warnings, inspiration_reference)
        for item in group
        if item.source_file
    }
    warnings: List[str] = []
    for item in canon_context:
        if item.status != "canon":
            warnings.append(f"Non-canon evidence found in canon_context: {item.evidence_id}")
    for label, group, expected in (
        ("draft_reference", draft_reference, "draft"),
        ("deprecated_warnings", deprecated_warnings, "deprecated"),
        ("inspiration_reference", inspiration_reference, "inspiration"),
    ):
        for item in group:
            if item.status != expected:
                warnings.append(f"Unexpected status in {label}: {item.evidence_id} has {item.status}")
    return Diagnostics(
        source_count=len(sources),
        evidence_count_by_status=counts,
        canon_count=counts["canon"],
        draft_count=counts["draft"],
        deprecated_count=counts["deprecated"],
        inspiration_count=counts["inspiration"],
        has_canon_evidence=bool(canon_context),
        warnings=warnings,
    )


def default_metadata() -> Dict[str, Any]:
    return {
        "schema_name": "v1_normalized_context_pack_candidate",
        "schema_version": "0.1-experimental",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "governance_rules": [
            "Canon is the only current truth source.",
            "Draft cannot enter canon_context.",
            "Deprecated cannot enter canon_context.",
            "Inspiration cannot enter canon_context.",
            "Unknown status requires human review.",
        ],
        "experiment": "normalized_context_schema",
    }
