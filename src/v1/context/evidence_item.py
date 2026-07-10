"""Evidence item schema for v1 Context Packs."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


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
