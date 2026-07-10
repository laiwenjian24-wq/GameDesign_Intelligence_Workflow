import json
from pathlib import Path

from experiments.normalized_context_adapter.build_context_pack_from_blocks import (
    build_context_pack,
    format_context_pack_markdown,
)
from experiments.normalized_context_adapter.evidence_adapter import (
    adapt_block_to_evidence,
    adapt_blocks_to_evidence,
    group_evidence_by_status,
)


def _block(status: str, text: str, source: str = "source.md", section: str = "Section"):
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


def test_evidence_adapter_preserves_core_fields():
    evidence = adapt_block_to_evidence(_block("canon", "Rin is a Nexus-7 replicant.", "rin.md", "Identity"))

    assert evidence["source_file"] == "rin.md"
    assert evidence["status"] == "canon"
    assert evidence["section_title"] == "Identity"
    assert evidence["status_priority"] == "highest"


def test_status_grouping_keeps_governance_boundaries():
    evidence = adapt_blocks_to_evidence(
        [
            _block("canon", "Canon fact."),
            _block("draft", "Draft note."),
            _block("deprecated", "Deprecated note."),
            _block("inspiration", "Inspiration note."),
        ]
    )

    grouped = group_evidence_by_status(evidence)

    assert len(grouped["canon_context"]) == 1
    assert len(grouped["draft_reference"]) == 1
    assert len(grouped["deprecated_warnings"]) == 1
    assert len(grouped["inspiration_reference"]) == 1


def test_deprecated_does_not_enter_canon_context(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [
            _block("deprecated", "Old Kite draft says Rin right leg injury.", "old_kite.md", "Old wound"),
        ],
    )

    context_pack = build_context_pack("Rin右腿受伤可以覆盖Canon吗？", blocks_path=blocks_path)

    assert context_pack["groups"]["canon_context"] == []
    assert context_pack["groups"]["deprecated_warnings"]


def test_missing_canon_evidence_is_rendered(tmp_path):
    blocks_path = _write_blocks(
        tmp_path,
        [
            _block("draft", "Draft note about Mouse and Rin.", "draft.md", "Dialogue"),
        ],
    )

    context_pack = build_context_pack("Snow是什么实验对象？", blocks_path=blocks_path)
    markdown = format_context_pack_markdown(context_pack)

    assert "## Missing Evidence" in markdown
    assert "No canon evidence found" in markdown


def test_dry_run_adapter_uses_no_deepseek(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    blocks_path = _write_blocks(
        tmp_path,
        [
            _block("canon", "Rin is a Nexus-7 replicant.", "rin.md", "Identity"),
            _block("draft", "Draft reference.", "draft.md", "Draft"),
        ],
    )

    context_pack = build_context_pack("Rin是什么身份？", blocks_path=blocks_path)

    assert context_pack["groups"]["canon_context"]
