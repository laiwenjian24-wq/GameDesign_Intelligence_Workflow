"""Tests for LLM-assisted query rewriting."""

from src.llm.client import FakeLLMClient
from src.rag.llm_query_rewriter import rewrite_query_for_retrieval


def test_llm_query_rewriter_rin_identity():
    plan = rewrite_query_for_retrieval("Rin是什么身份？", FakeLLMClient())

    assert plan.intent == "character_identity"
    assert plan.entities == ["Rin"]
    assert "Rin 身份 角色设定" in plan.rewritten_queries
    assert "Rin Nexus-7 android 仿生人" in plan.rewritten_queries
    assert "draft" in plan.forbidden_fact_statuses
    assert "deprecated" in plan.forbidden_fact_statuses
    assert "inspiration" in plan.forbidden_fact_statuses


def test_llm_query_rewriter_relationship():
    plan = rewrite_query_for_retrieval(
        "Rain和Second Foundation是什么关系？",
        FakeLLMClient(),
    )

    assert plan.intent == "relationship"
    assert plan.entities == ["Rain", "Second Foundation"]
    assert "Rain Second Foundation 关系" in plan.rewritten_queries
    assert "Rain 第二基金会 核心成员" in plan.rewritten_queries


def test_llm_query_rewriter_concept_definition():
    plan = rewrite_query_for_retrieval("Judgment Day是什么事件？", FakeLLMClient())

    assert plan.intent == "concept_definition"
    assert plan.entities == ["Judgment Day"]
    assert "Judgment Day 事件 定义" in plan.rewritten_queries
    assert "Judgment Day 世界观 时间线" in plan.rewritten_queries

