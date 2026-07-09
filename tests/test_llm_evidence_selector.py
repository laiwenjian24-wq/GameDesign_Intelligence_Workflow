"""Tests for LLM-assisted evidence selection."""

from src.llm.client import FakeLLMClient
from src.rag.llm_evidence_selector import select_evidence_for_context_pack
from src.rag.llm_query_rewriter import rewrite_query_for_retrieval


def test_evidence_selector_rejects_deprecated_as_fact():
    llm = FakeLLMClient()
    plan = rewrite_query_for_retrieval("Rin是什么身份？", llm)
    candidates = [
        {
            "source_file": "场景草稿_风筝（旧版）.md",
            "status": "deprecated",
            "text": "Deprecated old draft says Rin is Nexus-7.",
        },
        {
            "source_file": "故事大纲与角色设定.md",
            "status": "canon",
            "text": "Rin is Nexus-7.",
        },
    ]

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        plan,
        candidates,
        llm,
    )

    assert selection.selected_canon
    assert selection.selected_canon[0]["source_file"] == "故事大纲与角色设定.md"
    assert selection.selected_deprecated
    assert not any(
        item["source_file"] == "场景草稿_风筝（旧版）.md"
        for item in selection.selected_canon
    )


def test_evidence_selector_requires_canon_for_fact():
    llm = FakeLLMClient()
    plan = rewrite_query_for_retrieval("Rin是什么身份？", llm)
    candidates = [
        {
            "source_file": "分镜06_对白草稿.md",
            "status": "draft",
            "text": "Draft mentions Nexus-7.",
        }
    ]

    selection = select_evidence_for_context_pack(
        "Rin是什么身份？",
        plan,
        candidates,
        llm,
    )

    assert selection.selected_canon == []
    assert "insufficient canon evidence" in selection.warnings

