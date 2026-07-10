"""Normalize lightweight loaded documents into v1 NormalizedBlock objects."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from src.v1.ingestion.lite_document_loader import DocumentLoadResult
from src.v1.ingestion.normalized_block import NormalizedBlock
from src.v1.ingestion.status_policy import normalize_status


def load_manifest_status_map(manifest_path: str | Path | None) -> Dict[str, Dict[str, Any]]:
    if not manifest_path:
        return {}
    path = Path(manifest_path)
    if not path.exists():
        return {}
    items = json.loads(path.read_text(encoding="utf-8"))
    mapping: Dict[str, Dict[str, Any]] = {}
    for item in items:
        file_path = str(item.get("file_path", ""))
        if not file_path:
            continue
        keys = {
            file_path.lower(),
            str(Path(file_path)).lower(),
            Path(file_path).name.lower(),
        }
        for key in keys:
            mapping[key] = item
    return mapping


def normalize_document(
    document: DocumentLoadResult,
    manifest_metadata: Dict[str, Any] | None = None,
) -> List[NormalizedBlock]:
    manifest_metadata = manifest_metadata or {}
    status = normalize_status(manifest_metadata.get("status", document.metadata.get("status", "unknown")))
    blocks = _split_blocks(document.text)
    normalized: List[NormalizedBlock] = []
    for index, block in enumerate(blocks, start=1):
        metadata = {
            **document.metadata,
            "parser_used": document.parser_used,
            "parser_warnings": list(document.warnings),
            "asset_type": manifest_metadata.get("asset_type", ""),
            "tags": manifest_metadata.get("tags", []),
            "confidence": manifest_metadata.get("confidence", ""),
            "metadata_source": "import_manifest" if manifest_metadata else "none",
        }
        normalized.append(
            NormalizedBlock(
                block_id=f"{_slug(document.source_file)}::{index:04d}",
                source_file=document.source_file,
                original_path=document.original_path,
                status=status,
                document_type=document.document_type,
                section_title=block["section_title"],
                heading_path=block["heading_path"],
                page_number=block.get("page_number"),
                block_type=block["block_type"],
                text=block["text"],
                metadata=metadata,
            )
        )
    return normalized


def manifest_item_for_document(
    document: DocumentLoadResult,
    manifest_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    keys = [
        document.original_path.lower(),
        str(Path(document.original_path)).lower(),
        document.source_file.lower(),
    ]
    for key in keys:
        if key in manifest_map:
            return manifest_map[key]
    return {}


def normalize_documents(
    documents: Iterable[DocumentLoadResult],
    manifest_path: str | Path | None = None,
) -> List[NormalizedBlock]:
    manifest_map = load_manifest_status_map(manifest_path)
    blocks: List[NormalizedBlock] = []
    for document in documents:
        blocks.extend(normalize_document(document, manifest_item_for_document(document, manifest_map)))
    return blocks


def _split_blocks(text: str) -> List[Dict[str, Any]]:
    if not text.strip():
        return [
            {
                "section_title": "Metadata only",
                "heading_path": [],
                "block_type": "unknown",
                "text": "",
                "page_number": None,
            }
        ]

    blocks: List[Dict[str, Any]] = []
    heading_stack: List[str] = []
    section_title = "Document"
    buffer: List[str] = []

    def flush() -> None:
        nonlocal buffer
        content = "\n".join(buffer).strip()
        if not content:
            buffer = []
            return
        blocks.append(
            {
                "section_title": section_title,
                "heading_path": list(heading_stack),
                "block_type": _block_type(content),
                "text": content,
                "page_number": _page_number_from_heading(heading_stack),
            }
        )
        buffer = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip() or "Untitled"
            heading_stack = heading_stack[: max(level - 1, 0)]
            heading_stack.append(title)
            section_title = title
            blocks.append(
                {
                    "section_title": section_title,
                    "heading_path": list(heading_stack),
                    "block_type": "heading",
                    "text": title,
                    "page_number": _page_number_from_heading(heading_stack),
                }
            )
            continue
        if not stripped:
            flush()
            continue
        buffer.append(line)
    flush()
    return blocks


def _block_type(text: str) -> str:
    stripped = text.strip()
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) >= 2 and sum(1 for line in lines if "|" in line) >= 2:
        return "table_or_code"
    if stripped.startswith("```"):
        return "table_or_code"
    if all(line.startswith(("- ", "* ", "1. ")) for line in lines[: min(len(lines), 3)]):
        return "list"
    return "paragraph"


def _page_number_from_heading(heading_path: List[str]) -> int | None:
    for heading in reversed(heading_path):
        match = re.match(r"Page\s+(\d+)$", heading, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _slug(text: str) -> str:
    cleaned = re.sub(r"\s+", "-", text.strip())
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_.-]+", "", cleaned)
    return cleaned[:80] or "untitled"
