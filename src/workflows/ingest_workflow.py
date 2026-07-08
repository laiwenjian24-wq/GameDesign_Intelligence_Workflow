"""Narrative asset ingestion workflow placeholder."""

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from src.ingestion.load_markdown import load_markdown
from src.ingestion.load_txt import load_txt
from src.ingestion.scanner import scan_raw_assets
from src.metadata.classifier import classify_asset
from src.metadata.extractor import extract_metadata


IMPLEMENTED_EXTENSIONS = {".md", ".txt"}


def _project_root_from_processed_dir(processed_dir: Path) -> Path:
    """Resolve project root from knowledge_base/processed."""
    return processed_dir.resolve().parent.parent


def _load_import_manifest(processed_dir: Path) -> Dict[str, Dict]:
    """Load import_manifest.json if it exists."""
    manifest_path = (
        _project_root_from_processed_dir(processed_dir)
        / "knowledge_base"
        / "import_manifest.json"
    )
    if not manifest_path.exists():
        return {}

    raw_items = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = {}
    for item in raw_items:
        file_path = Path(item.get("file_path", ""))
        if not file_path:
            continue
        manifest[str(file_path.resolve()).lower()] = item
    return manifest


def _asset_id_for_path(path: Path, text: str) -> str:
    """Create a stable-ish asset id from path and content."""
    digest = hashlib.sha1(f"{path.as_posix()}\n{text}".encode("utf-8")).hexdigest()
    return f"asset_{digest[:16]}"


def _load_file(path: Path) -> dict:
    """Dispatch to the implemented first-version loader."""
    suffix = path.suffix.lower()
    if suffix == ".md":
        return load_markdown(path)
    if suffix == ".txt":
        return load_txt(path)
    raise ValueError(f"Unsupported first-version file type: {path}")


def _explicit_status_from_text(text: str) -> str:
    """Extract explicit status from simple note labels when present."""
    sample = text[:3000]
    patterns = [
        r"^\s*status\s*[:：]\s*(canon|draft|inspiration|deprecated|pattern|unknown)\s*$",
        r"^\s*状态\s*[:：]\s*(canon|draft|inspiration|deprecated|pattern|unknown)\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, sample, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).lower()
    return ""


def _domain_from_asset_type(asset_type: str, inferred_domain: str) -> str:
    """Map manifest asset_type to a first-pass detected_domain."""
    asset_type = (asset_type or "").lower()
    if asset_type in {
        "character",
        "worldbuilding",
        "location",
        "scene",
        "branch",
        "timeline",
        "dialogue",
        "deprecated",
        "inspiration",
    }:
        return "narrative"
    if asset_type in {"visual_reference", "prompt"}:
        return "visual"
    return inferred_domain


def _collect_ingestion_paths(raw_assets_dir: Path, manifest: Dict[str, Dict]) -> List[Path]:
    """Collect raw_assets files plus implemented manifest files."""
    paths = {str(path.resolve()).lower(): path for path in scan_raw_assets(raw_assets_dir)}

    for item in manifest.values():
        path = Path(item.get("file_path", ""))
        if path.exists() and path.suffix.lower() in IMPLEMENTED_EXTENSIONS:
            paths[str(path.resolve()).lower()] = path

    return [paths[key] for key in sorted(paths)]


def _build_record(path: Path, manifest_item: Dict) -> Tuple[Dict, str]:
    """Build one metadata record and return metadata_source."""
    loaded = _load_file(path)
    text = loaded["text"]
    source_metadata = {
        "source_path": loaded["source_path"],
        "file_name": loaded["file_name"],
        "file_type": loaded["file_type"],
    }

    classification = classify_asset(text, source_metadata)
    extracted = extract_metadata(text, source_metadata)
    explicit_status = _explicit_status_from_text(text)

    metadata_source = "inferred"
    status = classification["status"]
    tags = extracted["tags"]
    asset_type = ""
    reason = ""
    expected_usage = ""
    confidence = ""
    detected_domain = classification["detected_domain"]
    reason_used = "inferred: rule-based filename/path/text keyword classification"

    if explicit_status:
        metadata_source = "explicit"
        status = explicit_status
        reason_used = "explicit: Status label found in source text"

    if manifest_item:
        metadata_source = "manifest"
        status = manifest_item.get("status", status)
        asset_type = manifest_item.get("asset_type", "")
        tags = manifest_item.get("tags", tags)
        reason = manifest_item.get("reason", "")
        expected_usage = manifest_item.get("expected_usage", "")
        confidence = manifest_item.get("confidence", "")
        detected_domain = _domain_from_asset_type(asset_type, detected_domain)
        reason_used = f"manifest: {reason}" if reason else "manifest: import_manifest.json override"

    record = {
        "asset_id": _asset_id_for_path(path, text),
        "filename": loaded["file_name"],
        "source_file": loaded["file_name"],
        "file_path": loaded["source_path"],
        "file_type": loaded["file_type"],
        "asset_type": asset_type,
        "detected_domain": detected_domain,
        "status": status,
        "project": classification["project"],
        "related_characters": extracted["related_characters"],
        "related_locations": extracted["related_locations"],
        "related_branches": extracted["related_branches"],
        "tags": tags,
        "summary": extracted["summary"],
        "metadata_source": metadata_source,
        "confidence": confidence,
        "reason": reason,
        "expected_usage": expected_usage,
        "reason_used": reason_used,
    }
    return record, metadata_source


def _write_import_summary(records: List[Dict], processed_dir: Path) -> None:
    """Write a Markdown import summary."""
    manifest_count = sum(1 for record in records if record["metadata_source"] == "manifest")
    explicit_count = sum(1 for record in records if record["metadata_source"] == "explicit")
    inferred_count = sum(1 for record in records if record["metadata_source"] == "inferred")
    unconfirmed_count = sum(1 for record in records if record.get("status") == "unknown")

    lines = [
        "# Import Summary",
        "",
        f"- total_records: {len(records)}",
        f"- manifest覆盖数量: {manifest_count}",
        f"- explicit覆盖数量: {explicit_count}",
        f"- 自动推断数量: {inferred_count}",
        f"- 未确认数量: {unconfirmed_count}",
        "",
        "## Imported Records",
    ]

    for record in records:
        lines.append("")
        lines.append(f"- source_file: {record.get('source_file', '')}")
        lines.append(f"  - status: {record.get('status', '')}")
        lines.append(f"  - metadata_source: {record.get('metadata_source', '')}")
        lines.append(f"  - asset_type: {record.get('asset_type', '')}")
        lines.append(f"  - reason_used: {record.get('reason_used', '')}")

    (processed_dir / "import_summary.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def run_ingestion_workflow(raw_assets_dir: Path, processed_dir: Path) -> List[Dict]:
    """Run the first-stage ingestion workflow for Markdown and TXT files.

    Output is written to ``processed_dir / "metadata.jsonl"``.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "metadata.jsonl"
    manifest = _load_import_manifest(processed_dir)

    records: List[Dict] = []
    for path in _collect_ingestion_paths(raw_assets_dir, manifest):
        manifest_item = manifest.get(str(path.resolve()).lower(), {})
        record, _metadata_source = _build_record(path, manifest_item)
        records.append(record)

    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    _write_import_summary(records, processed_dir)
    return records
