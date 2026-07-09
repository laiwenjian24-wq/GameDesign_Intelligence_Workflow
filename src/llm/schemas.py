"""Schemas for LLM-assisted retrieval."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RetrievalPlan:
    """Structured query-understanding output for retrieval only."""

    original_question: str
    intent: str
    entities: List[str]
    rewritten_queries: List[str]
    preferred_source_types: List[str]
    forbidden_fact_statuses: List[str]
    confidence: str

    def to_dict(self) -> Dict:
        """Return a JSON-serializable representation."""
        return {
            "original_question": self.original_question,
            "intent": self.intent,
            "entities": list(self.entities),
            "rewritten_queries": list(self.rewritten_queries),
            "preferred_source_types": list(self.preferred_source_types),
            "forbidden_fact_statuses": list(self.forbidden_fact_statuses),
            "confidence": self.confidence,
        }


@dataclass
class EvidenceSelection:
    """Structured evidence selection for Context Pack grouping."""

    selected_canon: List[Dict] = field(default_factory=list)
    selected_draft: List[Dict] = field(default_factory=list)
    selected_deprecated: List[Dict] = field(default_factory=list)
    selected_inspiration: List[Dict] = field(default_factory=list)
    rejected: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Return a JSON-serializable representation."""
        return {
            "selected_canon": self.selected_canon,
            "selected_draft": self.selected_draft,
            "selected_deprecated": self.selected_deprecated,
            "selected_inspiration": self.selected_inspiration,
            "rejected": self.rejected,
            "warnings": self.warnings,
            "missing_evidence": self.missing_evidence,
        }


@dataclass
class QAAnswer:
    """Structured grounded answer for narrative QA experiments."""

    answer: str
    confidence: str
    canon_sources: List[str] = field(default_factory=list)
    draft_notes: List[str] = field(default_factory=list)
    deprecated_warnings: List[str] = field(default_factory=list)
    missing_evidence: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Return a JSON-serializable representation."""
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "canon_sources": list(self.canon_sources),
            "draft_notes": list(self.draft_notes),
            "deprecated_warnings": list(self.deprecated_warnings),
            "missing_evidence": list(self.missing_evidence),
            "limitations": list(self.limitations),
        }
