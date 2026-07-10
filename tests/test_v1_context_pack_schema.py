from src.v1.context.context_pack import ContextPack, ContextPackDiagnostics
from src.v1.context.evidence_item import EvidenceItem


def _evidence(status: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"{status}-001",
        source_file=f"{status}.md",
        original_path=f"/tmp/{status}.md",
        status=status,
        status_priority="highest" if status == "canon" else "reference only",
        section_title="Section",
        heading_path=["Root", "Section"],
        block_type="text",
        excerpt="Example excerpt",
        source_ref=f"{status}.md::Section",
        reason_used="schema test",
    )


def test_context_pack_can_hold_all_evidence_groups():
    pack = ContextPack(
        query="Rin是什么身份？",
        canon_context=[_evidence("canon")],
        draft_reference=[_evidence("draft")],
        deprecated_warnings=[_evidence("deprecated")],
        inspiration_reference=[_evidence("inspiration")],
        diagnostics=ContextPackDiagnostics(
            source_count=4,
            evidence_count_by_status={
                "canon": 1,
                "draft": 1,
                "deprecated": 1,
                "inspiration": 1,
            },
            canon_count=1,
            draft_count=1,
            deprecated_count=1,
            inspiration_count=1,
            has_canon_evidence=True,
        ),
    )

    assert pack.canon_context[0].status == "canon"
    assert pack.draft_reference[0].status == "draft"
    assert pack.deprecated_warnings[0].status == "deprecated"
    assert pack.inspiration_reference[0].status == "inspiration"
    assert pack.to_dict()["query"] == "Rin是什么身份？"
