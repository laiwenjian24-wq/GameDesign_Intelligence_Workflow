"""Dataclasses for continuity benchmark fixtures and results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class BenchmarkCase:
    case_id: str
    category: str
    input_text: str
    expected_decision: str
    expected_issue_types: List[str]
    required_evidence_statuses: List[str]
    forbidden_evidence_statuses: List[str]
    expected_source_policy: str
    notes: str
    allowed_decisions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "BenchmarkCase":
        allowed = payload.get("allowed_decisions") or [payload.get("expected_decision", "")]
        return cls(
            case_id=payload["case_id"],
            category=payload["category"],
            input_text=payload["input_text"],
            expected_decision=payload["expected_decision"],
            allowed_decisions=list(allowed),
            expected_issue_types=list(payload.get("expected_issue_types", [])),
            required_evidence_statuses=list(payload.get("required_evidence_statuses", [])),
            forbidden_evidence_statuses=list(payload.get("forbidden_evidence_statuses", [])),
            expected_source_policy=payload.get("expected_source_policy", ""),
            notes=payload.get("notes", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkResult:
    case_id: str
    input_text: str
    expected_decision: str
    actual_decision: str
    passed: bool
    expected_issue_types: List[str]
    actual_issue_types: List[str]
    notes: str
    allowed_decisions: List[str] = field(default_factory=list)
    failure_reasons: List[str] = field(default_factory=list)
    source_policy_notes: List[str] = field(default_factory=list)
    evidence_statuses_seen: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
