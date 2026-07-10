from src.v1.context.context_pack import (
    ContextPack,
    ContextPackDiagnostics,
    MissingEvidence,
)
from src.v1.context.context_pack_validator import validate_context_pack
from src.v1.context.evidence_item import EvidenceItem


def _evidence(status: str, source_file="source.md", section_title="Section") -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"{status}-001",
        source_file=source_file,
        original_path=f"/tmp/{source_file}",
        status=status,
        status_priority="highest" if status == "canon" else "reference only",
        section_title=section_title,
        heading_path=["Root", section_title],
        block_type="text",
        excerpt="Example excerpt",
        source_ref=f"{source_file}::{section_title}",
        reason_used="validator test",
    )


def _diagnostics():
    return ContextPackDiagnostics(
        source_count=1,
        evidence_count_by_status={
            "canon": 1,
            "draft": 0,
            "deprecated": 0,
            "inspiration": 0,
        },
        canon_count=1,
        has_canon_evidence=True,
    )


def test_non_canon_evidence_in_canon_context_fails_validation():
    for status in ("draft", "deprecated", "inspiration"):
        pack = ContextPack(
            query="test",
            canon_context=[_evidence(status)],
            diagnostics=_diagnostics(),
        )
        result = validate_context_pack(pack)
        assert result.valid is False
        assert result.errors


def test_missing_evidence_core_fields_fail_validation():
    pack = ContextPack(
        query="test",
        canon_context=[_evidence("canon", source_file="", section_title="")],
        diagnostics=_diagnostics(),
    )

    result = validate_context_pack(pack)

    assert result.valid is False
    assert any("missing source_file" in error for error in result.errors)
    assert any("missing section_title" in error for error in result.errors)


def test_empty_canon_context_requires_missing_evidence():
    pack = ContextPack(
        query="test",
        diagnostics=ContextPackDiagnostics(
            evidence_count_by_status={
                "canon": 0,
                "draft": 0,
                "deprecated": 0,
                "inspiration": 0,
            }
        ),
    )

    result = validate_context_pack(pack)

    assert result.valid is False
    assert any("missing_evidence is required" in error for error in result.errors)


def test_empty_canon_context_with_missing_evidence_can_validate():
    pack = ContextPack(
        query="test",
        missing_evidence=[
            MissingEvidence(description="No canon evidence found.", severity="high")
        ],
        diagnostics=ContextPackDiagnostics(
            evidence_count_by_status={
                "canon": 0,
                "draft": 0,
                "deprecated": 0,
                "inspiration": 0,
            }
        ),
    )

    result = validate_context_pack(pack)

    assert result.valid is True
