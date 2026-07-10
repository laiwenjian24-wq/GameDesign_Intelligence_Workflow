"""JSON Context Pack schema for v1."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from src.v1.context.evidence_item import EvidenceItem


@dataclass
class MissingEvidence:
    description: str
    severity: str = "medium"
    related_entities: List[str] = field(default_factory=list)
    suggested_next_step: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextPackDiagnostics:
    source_count: int = 0
    evidence_count_by_status: Dict[str, int] = field(default_factory=dict)
    canon_count: int = 0
    draft_count: int = 0
    deprecated_count: int = 0
    inspiration_count: int = 0
    has_canon_evidence: bool = False
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
    diagnostics: ContextPackDiagnostics = field(default_factory=ContextPackDiagnostics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    task_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
