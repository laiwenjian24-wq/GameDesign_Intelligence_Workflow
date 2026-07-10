"""Minimal claim and continuity issue schemas for the JSON pack experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Claim:
    claim_id: str
    raw_text: str
    subject: str
    attribute: str
    value: str
    confidence: float
    extraction_method: str
    branch_scope: Optional[str] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContinuityIssue:
    issue_id: str
    issue_type: str
    severity: str
    new_claim: Dict[str, Any]
    related_evidence: List[Dict[str, Any]]
    explanation: str
    suggested_fix: str
    source_policy: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
