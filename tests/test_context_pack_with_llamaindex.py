"""Tests for Context Pack compatibility with LlamaIndex retrieval."""

import json

from src.context.llamaindex_context_builder import build_context_pack_with_llamaindex
from src.rag.llamaindex_ingest import build_llamaindex_nodes


def _write_source(tmp_path, filename: str, text: str):
    path = tmp_path / filename
    path.write_text(text, encoding="utf-8")
    return path


def _manifest_item(path, status: str, asset_type: str, tags=None, reason=""):
    return {
        "file_path": str(path),
        "asset_type": asset_type,
        "status": status,
        "tags": tags or [],
        "reason": reason or f"{path.name} reason",
        "expected_usage": f"{status} usage",
    }


def _build_test_index(tmp_path):
    canon = _write_source(
        tmp_path,
        "rin_canon.md",
        "# Rin Canon\nRin identity is Nexus-7. Rin left leg injury is canon.",
    )
    deprecated = _write_source(
        tmp_path,
        "old_kite.md",
        "# Old Kite Draft\nDeprecated old Kite draft says Rin right leg injury.",
    )
    draft = _write_source(
        tmp_path,
        "draft_dialogue.md",
        "# Draft Dialogue\nDraft dialogue: Mouse asks Rin about wound care.",
    )
    manifest_path = tmp_path / "import_manifest.json"
    manifest_path.write_text(
        json.dumps(
            [
                _manifest_item(canon, "canon", "character", ["Rin", "identity", "injury"]),
                _manifest_item(deprecated, "deprecated", "deprecated", ["old Kite", "Rin"]),
                _manifest_item(draft, "draft", "dialogue", ["dialogue", "Mouse", "Rin"]),
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    index_dir = tmp_path / "llama_index"
    build_llamaindex_nodes(manifest_path, index_dir)
    return index_dir


def test_deprecated_old_kite_is_placed_into_deprecated_warnings(tmp_path):
    index_dir = _build_test_index(tmp_path)

    context_pack = build_context_pack_with_llamaindex(
        "old Kite Rin right leg injury",
        top_k=6,
        index_dir=index_dir,
    )

    assert any(
        item["source_file"] == "old_kite.md"
        for item in context_pack["deprecated_warnings"]
    )
    assert all(
        item["source_file"] != "old_kite.md"
        for item in context_pack["canon_context"]
    )


def test_draft_dialogue_is_not_placed_into_canon_context(tmp_path):
    index_dir = _build_test_index(tmp_path)

    context_pack = build_context_pack_with_llamaindex(
        "Mouse Rin wound care draft dialogue",
        top_k=6,
        index_dir=index_dir,
    )

    assert any(
        item["source_file"] == "draft_dialogue.md"
        for item in context_pack["draft_reference"]
    )
    assert all(
        item["source_file"] != "draft_dialogue.md"
        for item in context_pack["canon_context"]
    )


def test_context_pack_keeps_canon_draft_deprecated_separation(tmp_path):
    index_dir = _build_test_index(tmp_path)

    context_pack = build_context_pack_with_llamaindex(
        "Rin identity injury dialogue old Kite",
        top_k=8,
        index_dir=index_dir,
    )

    assert any(item["status"] == "canon" for item in context_pack["canon_context"])
    assert any(item["status"] == "draft" for item in context_pack["draft_reference"])
    assert any(
        item["status"] == "deprecated"
        for item in context_pack["deprecated_warnings"]
    )
    assert all(item["status"] == "canon" for item in context_pack["canon_context"])
    assert all(item["status"] == "draft" for item in context_pack["draft_reference"])
    assert all(
        item["status"] == "deprecated"
        for item in context_pack["deprecated_warnings"]
    )
    assert "retrieval_metadata" in context_pack
    assert context_pack["retrieval_metadata"]["retrieval_mode"] in {
        "bm25",
        "fallback",
    }
