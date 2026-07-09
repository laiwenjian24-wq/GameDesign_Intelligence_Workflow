"""Tests for the experimental LlamaIndex retrieval path."""

import json
from pathlib import Path

import pytest

from src.rag.llamaindex_ingest import (
    DEFAULT_MANIFEST_PATH,
    build_llamaindex_nodes,
    create_documents_from_manifest,
    is_real_llamaindex_available,
)
from src.rag.llamaindex_retriever import (
    is_real_bm25_available,
    retrieve_with_llamaindex,
)


def _write_source(tmp_path, filename: str, text: str):
    path = tmp_path / filename
    path.write_text(text, encoding="utf-8")
    return path


def _write_manifest(tmp_path, items):
    manifest_path = tmp_path / "import_manifest.json"
    manifest_path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return manifest_path


def _manifest_item(path, status: str, asset_type: str, tags=None, reason=""):
    return {
        "file_path": str(path),
        "asset_type": asset_type,
        "status": status,
        "tags": tags or [],
        "reason": reason or f"{path.name} reason",
        "expected_usage": f"{status} usage",
    }


def test_manifest_metadata_survives_into_llamaindex_nodes(tmp_path):
    source = _write_source(tmp_path, "rin_canon.md", "# Rin\nRin identity is Nexus-7.")
    manifest_path = _write_manifest(
        tmp_path,
        [_manifest_item(source, "canon", "character", ["Rin", "Nexus-7"])],
    )

    documents = create_documents_from_manifest(manifest_path)
    nodes = build_llamaindex_nodes(manifest_path, tmp_path / "llama_index")

    assert documents[0].metadata["source_file"] == "rin_canon.md"
    assert nodes[0]["metadata"]["source_file"] == "rin_canon.md"
    assert nodes[0]["metadata"]["status"] == "canon"
    assert nodes[0]["metadata"]["asset_type"] == "character"
    assert nodes[0]["metadata"]["tags"] == ["Rin", "Nexus-7"]
    assert nodes[0]["metadata"]["metadata_source"] == str(manifest_path)


def test_markdown_heading_metadata(tmp_path):
    source = _write_source(
        tmp_path,
        "characters.md",
        "# Characters\n\n### Rin [Nexus-7仿生人]\nRin is a Nexus-7 android.",
    )
    manifest_path = _write_manifest(
        tmp_path,
        [_manifest_item(source, "canon", "character", ["Rin", "Nexus-7"])],
    )

    nodes = build_llamaindex_nodes(manifest_path, tmp_path / "llama_index")
    rin_nodes = [
        node for node in nodes
        if node["metadata"].get("section_title") == "Rin [Nexus-7仿生人]"
    ]

    assert rin_nodes
    assert rin_nodes[0]["metadata"]["heading"] == "Rin [Nexus-7仿生人]"
    assert rin_nodes[0]["metadata"]["heading_path"] == [
        "Characters",
        "Rin [Nexus-7仿生人]",
    ]


def test_llamaindex_import_available_or_skip():
    if not is_real_llamaindex_available():
        pytest.skip(
            "LlamaIndex is not installed. Install llama-index and "
            "llama-index-retrievers-bm25 to run the real retrieval stack."
        )

    assert is_real_llamaindex_available()


def test_retrieve_rin_identity_returns_canon_nodes(tmp_path):
    canon = _write_source(tmp_path, "rin_canon.md", "# Rin\nRin identity is Nexus-7.")
    draft = _write_source(tmp_path, "rin_dialogue.md", "# Draft\nRin talks with Mouse.")
    manifest_path = _write_manifest(
        tmp_path,
        [
            _manifest_item(canon, "canon", "character", ["Rin", "identity"]),
            _manifest_item(draft, "draft", "dialogue", ["Rin", "Mouse"]),
        ],
    )
    index_dir = tmp_path / "llama_index"
    build_llamaindex_nodes(manifest_path, index_dir)

    results = retrieve_with_llamaindex(
        "Rin identity Nexus-7",
        top_k=4,
        index_dir=index_dir,
    )

    assert results
    assert results[0]["source_file"] == "rin_canon.md"
    assert results[0]["status"] == "canon"
    assert "Nexus-7" in results[0]["text"]


def test_bm25_retriever_uses_llamaindex(tmp_path):
    if not is_real_bm25_available():
        pytest.skip(
            "LlamaIndex BM25Retriever is not installed. Install "
            "llama-index-retrievers-bm25 to verify the real BM25 path."
        )

    canon = _write_source(tmp_path, "rin_canon.md", "# Rin\nRin identity is Nexus-7.")
    manifest_path = _write_manifest(
        tmp_path,
        [_manifest_item(canon, "canon", "character", ["Rin", "identity"])],
    )
    index_dir = tmp_path / "llama_index"
    build_llamaindex_nodes(manifest_path, index_dir)

    results = retrieve_with_llamaindex(
        "Rin identity Nexus-7",
        top_k=2,
        index_dir=index_dir,
    )

    assert results
    assert results[0]["retrieval_mode"] == "bm25"
    assert results[0]["used_real_llamaindex"] is True
    assert results[0]["fallback"] is False


def test_context_rag_rin_identity_uses_real_bm25_without_fallback(tmp_path):
    if not is_real_bm25_available():
        pytest.skip(
            "LlamaIndex BM25Retriever is not installed. This test verifies "
            "real project-data retrieval after dependencies are installed."
        )
    if not Path(DEFAULT_MANIFEST_PATH).exists():
        pytest.skip("Project import_manifest.json is not available.")

    index_dir = tmp_path / "llama_index"
    build_llamaindex_nodes(DEFAULT_MANIFEST_PATH, index_dir)

    results = retrieve_with_llamaindex("Rin是什么身份？", top_k=8, index_dir=index_dir)

    assert results
    assert all(result["retrieval_mode"] == "bm25" for result in results)
    assert all(result["used_real_llamaindex"] is True for result in results)
    assert all(result["fallback"] is False for result in results)
