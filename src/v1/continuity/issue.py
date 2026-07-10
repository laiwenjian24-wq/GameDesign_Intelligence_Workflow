"""Continuity issue schema for v1."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


ISSUE_TYPES = {
    "missing_canon_evidence",
    "deprecated_contamination",
    "draft_overrides_canon",
    "branch_state_conflict",
    "insufficient_evidence",
    "character_behavior_conflict",
    "tone_theme_conflict",
}


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
