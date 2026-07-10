"""Benchmark case schema for v1 regression fixtures."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class BenchmarkCase:
    case_id: str
    category: str
    input_text: str
    expected_decision: str
    allowed_decisions: List[str]
    expected_issue_types: List[str]
    required_evidence_statuses: List[str]
    forbidden_evidence_statuses: List[str]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
