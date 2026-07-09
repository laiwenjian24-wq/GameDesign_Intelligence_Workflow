"""Tests for LLM-assisted Context Pack construction."""

from pathlib import Path

import pytest

from src.context.llamaindex_context_builder import build_context_pack_with_llamaindex
from src.llm.client import FakeLLMClient
from src.rag.llamaindex_ingest import DEFAULT_MANIFEST_PATH, build_llamaindex_nodes
from src.rag.llamaindex_retriever import is_real_bm25_available


def test_llm_assisted_context_rin_identity_selects_canon(tmp_path):
    if not is_real_bm25_available():
        pytest.skip("Real LlamaIndex BM25 is required for this integration test.")
    if not Path(DEFAULT_MANIFEST_PATH).exists():
        pytest.skip("Project import_manifest.json is not available.")

    index_dir = tmp_path / "llama_index"
    build_llamaindex_nodes(DEFAULT_MANIFEST_PATH, index_dir)

    context_pack = build_context_pack_with_llamaindex(
        "Rin是什么身份？",
        top_k=8,
        index_dir=index_dir,
        use_llm_assist=True,
        llm_client=FakeLLMClient(),
    )

    source_files = {item["source_file"] for item in context_pack["canon_context"]}
    expected = {
        "故事大纲与角色设定.md",
        "STUPID游戏世界观设定集.md",
        "世界观概述.md",
    }
    assert context_pack["retrieval_plan"]["intent"] == "character_identity"
    assert source_files & expected
    assert context_pack["missing_evidence"] == []


def test_llm_assisted_context_keeps_status_separation(tmp_path):
    if not is_real_bm25_available():
        pytest.skip("Real LlamaIndex BM25 is required for this integration test.")
    if not Path(DEFAULT_MANIFEST_PATH).exists():
        pytest.skip("Project import_manifest.json is not available.")

    index_dir = tmp_path / "llama_index"
    build_llamaindex_nodes(DEFAULT_MANIFEST_PATH, index_dir)

    context_pack = build_context_pack_with_llamaindex(
        "Rin是什么身份？",
        top_k=8,
        index_dir=index_dir,
        use_llm_assist=True,
        llm_client=FakeLLMClient(),
    )

    assert all(item["status"] == "canon" for item in context_pack["canon_context"])
    assert all(
        item["status"] == "deprecated"
        for item in context_pack["deprecated_warnings"]
    )
    assert not any(
        item["status"] in {"draft", "deprecated", "inspiration"}
        for item in context_pack["canon_context"]
    )

