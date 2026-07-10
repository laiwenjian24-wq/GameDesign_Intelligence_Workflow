import json
from pathlib import Path

from experiments.normalized_context_schema.build_json_context_pack import build_json_context_pack
from experiments.normalized_context_schema.validate_context_pack import validate_context_pack


def _block(status: str, text: str, source: str, section: str):
    return {
        "block_id": f"{source}::0001",
        "source_file": source,
        "original_path": str(Path("tmp") / source),
        "status": status,
        "document_type": "md",
        "section_title": section,
        "heading_path": ["Root", section],
        "page_number": None,
        "block_type": "text",
        "text": text,
        "metadata": {"asset_type": "test", "tags": [status]},
    }


def _write_blocks(tmp_path: Path, blocks):
    path = tmp_path / "normalized_blocks.jsonl"
    path.write_text(
        "\n".join(json.dumps(block, ensure_ascii=False) for block in blocks) + "\n",
        encoding="utf-8",
    )
    return path


def test_json_context_pack_schema_includes_required_fields(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [_block("canon", "Rin is a Nexus-7 replicant.", "rin.md", "Identity")],
    )

    payload = build_json_context_pack("Rin是什么身份？", blocks_path=blocks_path)

    for field in (
        "query",
        "canon_context",
        "draft_reference",
        "deprecated_warnings",
        "inspiration_reference",
        "missing_evidence",
        "source_summary",
        "diagnostics",
        "metadata",
    ):
        assert field in payload


def test_non_canon_statuses_do_not_enter_canon_context(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [
            _block("draft", "Draft Rin note.", "draft.md", "Draft"),
            _block("deprecated", "Deprecated Rin note.", "old.md", "Old"),
            _block("inspiration", "Inspiration Rin note.", "idea.md", "Idea"),
        ],
    )

    payload = build_json_context_pack("Rin", blocks_path=blocks_path)

    assert payload["canon_context"] == []
    assert payload["draft_reference"]
    assert payload["deprecated_warnings"]
    assert payload["inspiration_reference"]


def test_evidence_items_preserve_source_status_and_section(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [_block("canon", "Snow is an experiment subject.", "snow.md", "Snow")],
    )

    payload = build_json_context_pack("Snow实验对象", blocks_path=blocks_path)
    item = payload["canon_context"][0]

    assert item["source_file"] == "snow.md"
    assert item["status"] == "canon"
    assert item["section_title"] == "Snow"


def test_missing_evidence_non_empty_when_no_canon(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [_block("draft", "Draft-only Snow note.", "draft.md", "Draft")],
    )

    payload = build_json_context_pack("Snow实验对象", blocks_path=blocks_path)

    assert payload["canon_context"] == []
    assert payload["missing_evidence"]


def test_diagnostics_counts_are_correct(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [
            _block("canon", "Rin identity.", "canon.md", "Identity"),
            _block("draft", "Rin draft.", "draft.md", "Draft"),
            _block("deprecated", "Rin old.", "old.md", "Old"),
            _block("inspiration", "Rin idea.", "idea.md", "Idea"),
        ],
    )

    payload = build_json_context_pack("Rin", blocks_path=blocks_path)
    diagnostics = payload["diagnostics"]

    assert diagnostics["canon_count"] == 1
    assert diagnostics["draft_count"] == 1
    assert diagnostics["deprecated_count"] == 1
    assert diagnostics["inspiration_count"] == 1
    assert diagnostics["has_canon_evidence"] is True
    assert validate_context_pack(payload)["valid"] is True
