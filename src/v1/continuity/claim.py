"""Claim schema for v1 continuity workflows."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Claim:
    claim_id: str
    raw_text: str
    subject: str
    attribute: str
    value: str
    confidence: float
    extraction_method: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    branch_scope: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
