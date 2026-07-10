"""Minimal JSON-backed knowledge index for v1 Lite KB MVP."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from src.v1.ingestion.lite_document_loader import (
    SUPPORTED_EXTENSIONS,
    DocumentLoadResult,
    available_parsers,
    load_document,
)
from src.v1.ingestion.lite_normalizer import normalize_document, normalize_documents_with_diagnostics
from src.v1.ingestion.manifest_status_resolver import (
    ManifestStatusResolver,
    first_entry_path,
    has_suspected_mojibake,
    inspect_manifest,
    resolve_entry_path,
)
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
    blocks, manifest_diagnostics = normalize_documents_with_diagnostics(
        documents,
        manifest_path=manifest_path,
        project_root=Path.cwd(),
    )
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
            "manifest_status_diagnostics": manifest_diagnostics,
        },
    )


def build_lite_index_from_manifest(
    manifest_path: str | Path,
    include_ext: Iterable[str] | None = None,
) -> LiteKnowledgeBase:
    manifest = Path(manifest_path)
    allowed = {
        ext.lower() if str(ext).startswith(".") else f".{str(ext).lower()}"
        for ext in (include_ext or SUPPORTED_EXTENSIONS)
    }
    resolver = ManifestStatusResolver(manifest_path=manifest, project_root=Path.cwd())
    documents: List[DocumentLoadResult] = []
    blocks: List[NormalizedBlock] = []
    loaded_records: List[Dict[str, Any]] = []
    missing_files: List[Dict[str, Any]] = []
    skipped_files: List[Dict[str, Any]] = []
    existing_count = 0
    suspected_mojibake_count = 0

    for entry_index, entry in enumerate(resolver.entries):
        raw_path = first_entry_path(entry)
        if has_suspected_mojibake(raw_path):
            suspected_mojibake_count += 1
        resolved_path = resolve_entry_path(entry, resolver.manifest_parent)
        extension = resolved_path.suffix.lower()
        if extension not in allowed:
            skipped_files.append(
                {
                    "index": entry_index,
                    "path": raw_path,
                    "resolved_path": str(resolved_path),
                    "reason": f"extension_not_included: {extension or '<none>'}",
                }
            )
            continue
        try:
            exists = resolved_path.exists() and resolved_path.is_file()
        except OSError:
            exists = False
        if not exists:
            missing_files.append(
                {
                    "index": entry_index,
                    "path": raw_path,
                    "resolved_path": str(resolved_path),
                    "status": entry.get("status", "unknown"),
                    "suspected_mojibake": has_suspected_mojibake(raw_path),
                }
            )
            continue
        existing_count += 1
        document = load_document(resolved_path)
        documents.append(document)
        resolution = resolver.resolution_from_manifest_entry_direct(entry)
        loaded_records.append(
            {
                "source_file": document.source_file,
                "status": resolution.status,
                "method": resolution.method,
                "manifest_matched_path": resolution.manifest_matched_path,
            }
        )
        blocks.extend(normalize_document(document, resolution.manifest_entry or {}, resolution))

    block_dicts = [block.to_dict() for block in blocks]
    status_counts: Dict[str, int] = {}
    for block in block_dicts:
        status_counts[block["status"]] = status_counts.get(block["status"], 0) + 1
    warnings = [
        {"source_file": document.source_file, "warnings": document.warnings}
        for document in documents
        if document.warnings
    ]
    doctor = inspect_manifest(manifest)
    manifest_driven_metadata = {
        "enabled": True,
        "manifest_path": str(manifest),
        "entries_loaded": len(resolver.entries),
        "files_existing": existing_count,
        "files_missing": len(missing_files),
        "files_loaded": len(documents),
        "missing_files": missing_files[:10],
        "skipped_files": skipped_files[:10],
        "suspected_mojibake_count": suspected_mojibake_count,
        "status_counts": status_counts,
        "parser_availability": available_parsers(),
    }
    if resolver.entries and existing_count == 0:
        warnings.append(
            {
                "source_file": str(manifest),
                "warnings": [
                    "No manifest files exist on disk. Check manifest path encoding or source file locations."
                ],
            }
        )

    return LiteKnowledgeBase(
        blocks=block_dicts,
        source_count=len({document.source_file for document in documents}),
        status_counts=status_counts,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata={
            "input_paths": [],
            "manifest_path": str(manifest),
            "include_ext": sorted(allowed),
            "loaded_file_count": len(documents),
            "skipped_file_count": len(skipped_files),
            "warnings": warnings,
            "manifest_status_diagnostics": {
                "manifest_path": str(manifest),
                "manifest_entries_loaded": len(resolver.entries),
                "matched_file_count": len(documents),
                "unmatched_file_count": len(missing_files),
                "ambiguous_file_count": 0,
                "matched_files": loaded_records[:10],
                "unmatched_files": missing_files[:10],
                "ambiguous_files": [],
            },
            "manifest_driven_ingest": manifest_driven_metadata,
            "manifest_doctor": {
                key: value
                for key, value in doctor.items()
                if key != "entries"
            },
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
