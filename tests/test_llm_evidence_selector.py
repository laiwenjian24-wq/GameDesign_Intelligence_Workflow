"""Tests for LLM-assisted evidence selection."""

from src.llm.client import FakeLLMClient, LLMResponse
from src.rag.llm_evidence_selector import select_evidence_for_context_pack
from src.rag.llm_query_rewriter import rewrite_query_for_retrieval


class CapturingLLMClient:
    def __init__(self, response_text):
        self.response_text = response_text
        self.context = None

    def complete(self, prompt, context=None):
        self.context = context or {}
        return LLMResponse(text=self.response_text, metadata={"provider": "capture"})


def _plan():
    return rewrite_query_for_retrieval("Rin是什么身份？", FakeLLMClient())


def test_evidence_selector_rejects_deprecated_as_fact():
    llm = FakeLLMClient()
    candidates = [
        {
            "source_file": "old_draft.md",
            "status": "deprecated",
            "excerpt": "Deprecated old draft says Rin is Nexus-7.",
            "text": "Deprecated old draft says Rin is Nexus-7.",
        },
        {
            "source_file": "rin_canon.md",
            "status": "canon",
            "excerpt": "Rin is Nexus-7.",
            "text": "Rin is Nexus-7.",
        },
    ]

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        _plan(),
        candidates,
        llm,
    )

    assert selection.selected_canon
    assert selection.selected_canon[0]["source_file"] == "rin_canon.md"
    assert selection.selected_deprecated
    assert not any(
        item["source_file"] == "old_draft.md"
        for item in selection.selected_canon
    )


def test_evidence_selector_requires_canon_for_fact():
    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        _plan(),
        [
            {
                "source_file": "draft_dialogue.md",
                "status": "draft",
                "excerpt": "Draft mentions Nexus-7.",
                "text": "Draft mentions Nexus-7.",
            }
        ],
        FakeLLMClient(),
    )

    assert selection.selected_canon == []
    assert "insufficient canon evidence" in selection.warnings
    assert "no canon evidence selected" in selection.missing_evidence


def test_evidence_selector_returns_ids_not_full_text():
    llm = CapturingLLMClient(
        '{"selected_canon_ids":["c001"],"selected_draft_ids":[],'
        '"selected_deprecated_ids":[],"selected_inspiration_ids":[],'
        '"rejected_ids":[],"warnings":[],"missing_evidence":[]}'
    )
    long_text = "Rin is Nexus-7.\n" * 100

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        _plan(),
        [
            {
                "source_file": "canon.md",
                "status": "canon",
                "excerpt": "Rin is Nexus-7.",
                "text": long_text,
                "score": 1.0,
            }
        ],
        llm,
    )

    compact_candidate = llm.context["candidates"][0]
    assert compact_candidate["candidate_id"] == "c001"
    assert "text" not in compact_candidate
    assert selection.selected_canon[0]["text"] == long_text


def test_evidence_selector_maps_ids_back_to_candidates():
    llm = CapturingLLMClient(
        '{"selected_canon_ids":["c001"],"selected_draft_ids":[],'
        '"selected_deprecated_ids":[],"selected_inspiration_ids":[],'
        '"rejected_ids":[],"warnings":[],"missing_evidence":[]}'
    )

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        _plan(),
        [
            {
                "source_file": "canon.md",
                "status": "canon",
                "excerpt": "Rin is Nexus-7.",
                "text": "full text retained by Python",
            }
        ],
        llm,
    )

    assert selection.selected_canon[0]["candidate_id"] == "c001"
    assert selection.selected_canon[0]["text"] == "full text retained by Python"


def test_unknown_candidate_id_is_ignored_with_warning():
    llm = CapturingLLMClient(
        '{"selected_canon_ids":["c999"],"selected_draft_ids":[],'
        '"selected_deprecated_ids":[],"selected_inspiration_ids":[],'
        '"rejected_ids":[],"warnings":[],"missing_evidence":[]}'
    )

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        _plan(),
        [{"source_file": "canon.md", "status": "canon", "excerpt": "Rin"}],
        llm,
    )

    assert selection.selected_canon == []
    assert any("unknown candidate_id ignored: c999" in item for item in selection.warnings)


def test_deprecated_id_does_not_enter_canon_context():
    llm = CapturingLLMClient(
        '{"selected_canon_ids":["c001"],"selected_draft_ids":[],'
        '"selected_deprecated_ids":[],"selected_inspiration_ids":[],'
        '"rejected_ids":[],"warnings":[],"missing_evidence":[]}'
    )

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        _plan(),
        [{"source_file": "old.md", "status": "deprecated", "excerpt": "Rin"}],
        llm,
    )

    assert selection.selected_canon == []
    assert any("cannot be selected as canon" in item for item in selection.warnings)

