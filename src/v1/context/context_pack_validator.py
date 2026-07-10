"""Validation helpers for v1 JSON Context Packs."""

from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List

from src.v1.context.context_pack import ContextPack
from src.v1.context.evidence_item import EvidenceItem
from src.v1.ingestion.status_policy import (
    CANON,
    DEPRECATED,
    DRAFT,
    INSPIRATION,
    can_enter_canon_context,
    normalize_status,
)


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


def _validate_required_evidence_fields(
    section_name: str,
    evidence_items: Iterable[EvidenceItem],
    errors: List[str],
) -> None:
    for index, item in enumerate(evidence_items, start=1):
        if not item.source_file:
            errors.append(f"{section_name}[{index}] missing source_file")
        if not item.status:
            errors.append(f"{section_name}[{index}] missing status")
        if not item.section_title:
            errors.append(f"{section_name}[{index}] missing section_title")


def _validate_group_status(
    section_name: str,
    evidence_items: Iterable[EvidenceItem],
    expected_status: str,
    errors: List[str],
) -> None:
    for index, item in enumerate(evidence_items, start=1):
        actual = normalize_status(item.status)
        if actual != expected_status:
            errors.append(
                f"{section_name}[{index}] has status {actual}; expected {expected_status}"
            )


def validate_context_pack(context_pack: ContextPack) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    for index, item in enumerate(context_pack.canon_context, start=1):
        if not can_enter_canon_context(item.status):
            errors.append(
                f"canon_context[{index}] has non-canon status {normalize_status(item.status)}"
            )

    groups = {
        "canon_context": (context_pack.canon_context, CANON),
        "draft_reference": (context_pack.draft_reference, DRAFT),
        "deprecated_warnings": (context_pack.deprecated_warnings, DEPRECATED),
        "inspiration_reference": (context_pack.inspiration_reference, INSPIRATION),
    }

    for section_name, (items, expected_status) in groups.items():
        _validate_required_evidence_fields(section_name, items, errors)
        _validate_group_status(section_name, items, expected_status, errors)

    if not context_pack.canon_context and not context_pack.missing_evidence:
        errors.append("missing_evidence is required when canon_context is empty")

    counts = context_pack.diagnostics.evidence_count_by_status
    if not counts:
        errors.append("diagnostics.evidence_count_by_status is required")
    else:
        for status in (CANON, DRAFT, DEPRECATED, INSPIRATION):
            if status not in counts:
                warnings.append(
                    f"diagnostics.evidence_count_by_status missing {status}"
                )

    return ValidationResult(valid=not errors, errors=errors, warnings=warnings)
