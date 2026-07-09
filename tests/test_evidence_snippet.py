"""Tests for evidence excerpt refinement."""

from src.llm.schemas import RetrievalPlan
from src.rag.evidence_snippet import refine_evidence_excerpt


def _rin_identity_plan():
    return RetrievalPlan(
        original_question="Rin是什么身份？",
        intent="character_identity",
        entities=["Rin"],
        rewritten_queries=["Rin 身份 角色设定"],
        preferred_source_types=["character"],
        forbidden_fact_statuses=["draft", "deprecated", "inspiration"],
        confidence="high",
    )


def test_refined_excerpt_does_not_change_status():
    candidate = {
        "status": "canon",
        "text": "### Rin [Nexus-7仿生人]\nRin 是 Nexus-7 仿生人。",
        "metadata": {"heading": "Rin [Nexus-7仿生人]"},
    }

    before_status = candidate["status"]
    excerpt = refine_evidence_excerpt(candidate, _rin_identity_plan())

    assert candidate["status"] == before_status
    assert "Rin" in excerpt
    assert "Nexus-7" in excerpt

