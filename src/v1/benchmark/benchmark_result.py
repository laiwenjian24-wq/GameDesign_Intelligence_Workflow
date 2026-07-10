"""Benchmark result schema for v1 regression fixtures."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
