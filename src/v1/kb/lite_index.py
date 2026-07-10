"""Minimal JSON-backed knowledge index for v1 Lite KB MVP."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from src.v1.ingestion.lite_document_loader import SUPPORTED_EXTENSIONS, DocumentLoadResult, load_document
from src.v1.ingestion.lite_normalizer import normalize_documents
from src.v1.ingestion.normalized_block import NormalizedBlock


DEFAULT_OUTPUT_PATH = Path("processed") / "v1_lite_kb.json"


@dataclass
class LiteKnowledgeBase:
    blocks: List[Dict[str, Any]]
    source_count: int
    status_counts: Dict[str, int]
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def collect_input_files(input_paths: Iterable[str | Path], include_ext: Iterable[str] | None = None) -> List[Path]:
    allowed = {ext.lower() if str(ext).startswith(".") else f".{str(ext).lower()}" for ext in (include_ext or SUPPORTED_EXTENSIONS)}
    files: List[Path] = []
    for input_path in input_paths:
        path = Path(input_path)
        if path.is_file():
            if path.suffix.lower() in allowed:
                files.append(path)
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in allowed:
                    files.append(child)
    return sorted(set(files), key=lambda item: str(item).lower())


def build_lite_index(
    input_paths: List[str | Path],
    manifest_path: str | Path | None = None,
    include_ext: Iterable[str] | None = None,
) -> LiteKnowledgeBase:
    files = collect_input_files(input_paths, include_ext=include_ext)
    documents: List[DocumentLoadResult] = [load_document(path) for path in files]
    blocks: List[NormalizedBlock] = normalize_documents(documents, manifest_path=manifest_path)
    block_dicts = [block.to_dict() for block in blocks]
    status_counts: Dict[str, int] = {}
    for block in block_dicts:
        status_counts[block["status"]] = status_counts.get(block["status"], 0) + 1
    warnings = [
        {"source_file": document.source_file, "warnings": document.warnings}
        for document in documents
        if document.warnings
    ]
    return LiteKnowledgeBase(
        blocks=block_dicts,
        source_count=len({document.source_file for document in documents}),
        status_counts=status_counts,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata={
            "input_paths": [str(path) for path in input_paths],
            "manifest_path": str(manifest_path) if manifest_path else "",
            "include_ext": sorted(
                ext.lower() if str(ext).startswith(".") else f".{str(ext).lower()}"
                for ext in (include_ext or SUPPORTED_EXTENSIONS)
            ),
            "loaded_file_count": len(documents),
            "skipped_file_count": 0,
            "warnings": warnings,
        },
    )


def save_lite_index(kb: LiteKnowledgeBase, output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(kb.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_lite_index(output_path: str | Path = DEFAULT_OUTPUT_PATH) -> LiteKnowledgeBase:
    payload = json.loads(Path(output_path).read_text(encoding="utf-8"))
    return LiteKnowledgeBase(
        blocks=list(payload.get("blocks", [])),
        source_count=int(payload.get("source_count", 0)),
        status_counts=dict(payload.get("status_counts", {})),
        created_at=str(payload.get("created_at", "")),
        metadata=dict(payload.get("metadata", {}) or {}),
    )
