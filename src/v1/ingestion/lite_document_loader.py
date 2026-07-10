"""Lightweight document loader for the v1 Lite Knowledge Base MVP."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


SUPPORTED_EXTENSIONS = {".md", ".txt", ".docx", ".pdf"}


@dataclass
class DocumentLoadResult:
    source_file: str
    original_path: str
    document_type: str
    text: str
    parser_used: str
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_document(path: str | Path) -> DocumentLoadResult:
    source_path = Path(path)
    extension = source_path.suffix.lower()
    metadata = {
        "extension": extension,
        "file_size": source_path.stat().st_size if source_path.exists() else None,
    }

    if not source_path.exists() or not source_path.is_file():
        return DocumentLoadResult(
            source_file=source_path.name,
            original_path=str(source_path),
            document_type=extension.lstrip(".") or "unknown",
            text="",
            parser_used="none",
            warnings=[f"file_not_found: {source_path}"],
            metadata=metadata,
        )

    if extension in {".md", ".txt"}:
        text, warning = _read_text_file(source_path)
        warnings = [warning] if warning else []
        return DocumentLoadResult(
            source_file=source_path.name,
            original_path=str(source_path),
            document_type=extension.lstrip("."),
            text=text,
            parser_used="direct_text",
            warnings=warnings,
            metadata=metadata,
        )

    if extension in {".docx", ".pdf"}:
        markitdown_result = _try_markitdown(source_path)
        if markitdown_result is not None:
            text, parser_warning = markitdown_result
            warnings = [parser_warning] if parser_warning else []
            return DocumentLoadResult(
                source_file=source_path.name,
                original_path=str(source_path),
                document_type=extension.lstrip("."),
                text=text,
                parser_used="markitdown",
                warnings=warnings,
                metadata=metadata,
            )

        if extension == ".pdf":
            pymupdf_result = _try_pymupdf(source_path)
            if pymupdf_result is not None:
                text, parser_warning = pymupdf_result
                warnings = ["markitdown_not_installed_or_failed"]
                if parser_warning:
                    warnings.append(parser_warning)
                return DocumentLoadResult(
                    source_file=source_path.name,
                    original_path=str(source_path),
                    document_type="pdf",
                    text=text,
                    parser_used="pymupdf",
                    warnings=warnings,
                    metadata=metadata,
                )

        return DocumentLoadResult(
            source_file=source_path.name,
            original_path=str(source_path),
            document_type=extension.lstrip("."),
            text="",
            parser_used="unsupported",
            warnings=[
                "markitdown_not_installed_or_failed",
                f"unsupported_without_parser: {extension}",
            ],
            metadata=metadata,
        )

    return DocumentLoadResult(
        source_file=source_path.name,
        original_path=str(source_path),
        document_type=extension.lstrip(".") or "unknown",
        text="",
        parser_used="unsupported",
        warnings=[f"unsupported_extension: {extension or '<none>'}"],
        metadata=metadata,
    )


def _read_text_file(path: Path) -> tuple[str, str]:
    encodings = ("utf-8-sig", "utf-8", "gb18030", "cp936")
    last_error = ""
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding), (
                "" if encoding in {"utf-8-sig", "utf-8"} else f"encoding_fallback: {encoding}"
            )
        except UnicodeDecodeError as exc:
            last_error = str(exc)
    return path.read_text(encoding="utf-8", errors="replace"), f"encoding_replace: {last_error}"


def _try_markitdown(path: Path) -> tuple[str, str] | None:
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError:
        return None
    try:
        result = MarkItDown().convert(str(path))
        text = getattr(result, "text_content", "") or str(result)
        return text, ""
    except Exception as exc:
        return "", f"markitdown_failed: {exc}"


def _try_pymupdf(path: Path) -> tuple[str, str] | None:
    try:
        import fitz  # type: ignore
    except ImportError:
        return None
    try:
        parts: List[str] = []
        with fitz.open(str(path)) as document:
            for page_number, page in enumerate(document, start=1):
                parts.append(f"\n\n# Page {page_number}\n\n")
                parts.append(page.get_text())
        return "".join(parts), ""
    except Exception as exc:
        return "", f"pymupdf_failed: {exc}"


def available_parsers() -> Dict[str, bool]:
    return {
        "markitdown": _module_available("markitdown"),
        "pymupdf": _module_available("fitz"),
    }


def _module_available(module_name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(module_name) is not None
