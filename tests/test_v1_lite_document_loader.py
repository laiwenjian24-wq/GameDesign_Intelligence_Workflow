from pathlib import Path

from src.v1.ingestion.lite_document_loader import load_document
from src.v1.ingestion.lite_normalizer import normalize_document


def test_lite_loader_reads_markdown_and_text(tmp_path):
    md = tmp_path / "note.md"
    txt = tmp_path / "note.txt"
    md.write_text("# Rin\n\nRin is Nexus-7.", encoding="utf-8")
    txt.write_text("Mouse injury note.", encoding="utf-8")

    md_result = load_document(md)
    txt_result = load_document(txt)

    assert md_result.text.startswith("# Rin")
    assert txt_result.text == "Mouse injury note."
    assert md_result.parser_used == "direct_text"
    assert txt_result.parser_used == "direct_text"


def test_lite_loader_docx_pdf_missing_parser_graceful(monkeypatch, tmp_path):
    monkeypatch.setattr("src.v1.ingestion.lite_document_loader._try_markitdown", lambda _path: None)
    monkeypatch.setattr("src.v1.ingestion.lite_document_loader._try_pymupdf", lambda _path: None)
    docx = tmp_path / "file.docx"
    pdf = tmp_path / "file.pdf"
    docx.write_bytes(b"fake")
    pdf.write_bytes(b"fake")

    docx_result = load_document(docx)
    pdf_result = load_document(pdf)

    assert docx_result.parser_used == "unsupported"
    assert pdf_result.parser_used == "unsupported"
    assert docx_result.warnings
    assert pdf_result.warnings


def test_lite_loader_unsupported_extension_graceful(tmp_path):
    source = tmp_path / "script.rpy"
    source.write_text("label start:", encoding="utf-8")

    result = load_document(source)

    assert result.parser_used == "unsupported"
    assert "unsupported_extension" in result.warnings[0]


def test_lite_normalizer_outputs_normalized_blocks(tmp_path):
    source = tmp_path / "note.md"
    source.write_text("# Rin\n\nRin is Nexus-7.\n\n- restrained", encoding="utf-8")
    result = load_document(source)

    blocks = normalize_document(result, {"status": "canon", "asset_type": "character"})

    assert blocks
    assert blocks[0].source_file == "note.md"
    assert blocks[0].status == "canon"
    assert blocks[0].section_title == "Rin"
