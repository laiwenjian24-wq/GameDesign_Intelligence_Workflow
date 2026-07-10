import json
from pathlib import Path

from experiments.docling_real_parser_adapter.docling_real_parse import (
    _manifest_item_for_input,
    parse_one_item,
)
from experiments.docling_real_parser_adapter.docling_to_normalized_blocks import (
    normalize_summary_payload,
)


def test_docling_missing_graceful_fallback(tmp_path):
    source = tmp_path / "sample.md"
    source.write_text("# Title\n\nText", encoding="utf-8")
    item = _manifest_item_for_input(source)

    result = parse_one_item(item, converter_cls=None)

    assert result["parser"] == "docling_not_installed"
    assert "Install with:" in result["messages"][1]


def test_fake_docling_like_structure_converts_to_normalized_blocks():
    payload = {
        "results": [
            {
                "parser": "docling",
                "source_file": "sample.md",
                "original_path": "sample.md",
                "status": "canon",
                "document_type": "md",
                "source_available": True,
                "content": {
                    "markdown": "# Title\n\nParagraph.\n\n| A | B |\n|---|---|\n| 1 | 2 |",
                    "headings": ["# Title"],
                    "tables": [],
                    "images": [],
                    "pages": [],
                },
                "manifest_metadata": {"asset_type": "test", "tags": ["Rin"]},
                "messages": [],
            }
        ]
    }

    blocks = normalize_summary_payload(payload)

    assert blocks
    assert blocks[0].source_file == "sample.md"
    assert blocks[0].status == "canon"
    assert blocks[0].section_title == "Title"
    assert blocks[0].block_type == "text"
    assert any(block.block_type == "table" for block in blocks)


def test_normalized_blocks_preserve_required_fields():
    payload = {
        "results": [
            {
                "parser": "docling",
                "source_file": "source.pdf",
                "original_path": "source.pdf",
                "status": "draft",
                "document_type": "pdf",
                "source_available": True,
                "content": {"markdown": "Body only", "tables": [], "images": [], "pages": []},
                "manifest_metadata": {},
                "messages": [],
            }
        ]
    }

    blocks = normalize_summary_payload(payload)

    for block in blocks:
        assert block.source_file
        assert block.status
        assert block.section_title
        assert block.block_type


def test_missing_docling_structure_marks_metadata_flags():
    payload = {
        "results": [
            {
                "parser": "docling",
                "source_file": "source.pdf",
                "original_path": "source.pdf",
                "status": "canon",
                "document_type": "pdf",
                "source_available": True,
                "content": {"markdown": "Body only", "tables": [], "images": [], "pages": []},
                "manifest_metadata": {},
                "messages": [],
            }
        ]
    }

    block = normalize_summary_payload(payload)[0]

    assert block.metadata["missing_heading_info"] is True
    assert block.metadata["missing_page_number"] is True
    assert block.metadata["missing_table_info"] is True


def test_adapter_does_not_modify_knowledge_base(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("# Source\n\nText", encoding="utf-8")
    before = source.read_text(encoding="utf-8")
    item = _manifest_item_for_input(source)

    result = parse_one_item(item, converter_cls=None)
    payload = {"results": [result]}
    normalize_summary_payload(payload)

    assert source.read_text(encoding="utf-8") == before
