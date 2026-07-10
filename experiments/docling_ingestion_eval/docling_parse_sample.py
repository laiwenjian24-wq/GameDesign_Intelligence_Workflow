"""Isolated Docling ingestion sample parser for v1 experiments.

The default dry-run path uses only the Python standard library. Real Docling
parsing is attempted only when --real is supplied and docling is installed.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "knowledge_base" / "import_manifest.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "sample_outputs"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "docling_parse_results.json"

PREFERRED_SAMPLE_NAMES = (
    "STUPID游戏世界观设定集.md",
    "故事大纲与角色设定.md",
    "任务设计_风筝.md",
)
PREFERRED_SAMPLE_PROFILES = (
    {"worldbuilding"},
    {"story_outline", "character"},
    {"quest_design", "kite", "branch"},
)
SUPPORTED_EXTENSIONS = {".md", ".docx", ".pdf", ".jpg", ".jpeg", ".png"}


def load_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> List[Dict[str, Any]]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _display_name(path_text: str) -> str:
    return Path(path_text).name


def _document_type(path_text: str) -> str:
    suffix = Path(path_text).suffix.lower().lstrip(".")
    return suffix or "unknown"


def select_candidates(
    manifest_items: Iterable[Dict[str, Any]],
    limit: int = 6,
) -> List[Dict[str, Any]]:
    items = list(manifest_items)
    selected: List[Dict[str, Any]] = []
    seen_paths = set()

    def add_item(item: Dict[str, Any]) -> None:
        path_text = item.get("file_path", "")
        if not path_text or path_text in seen_paths:
            return
        selected.append(item)
        seen_paths.add(path_text)

    for preferred_name in PREFERRED_SAMPLE_NAMES:
        for item in items:
            if _display_name(item.get("file_path", "")) == preferred_name:
                add_item(item)

    for profile in PREFERRED_SAMPLE_PROFILES:
        for item in items:
            metadata_terms = {
                str(item.get("asset_type", "")).lower(),
                *(str(tag).lower() for tag in item.get("tags", [])),
            }
            if profile.issubset(metadata_terms) or profile.intersection(metadata_terms):
                add_item(item)
                break

    for status in ("draft", "deprecated", "inspiration"):
        for item in items:
            if str(item.get("status", "")).lower() == status:
                add_item(item)
                break

    for item in items:
        path_text = item.get("file_path", "")
        if Path(path_text).suffix.lower() in SUPPORTED_EXTENSIONS:
            add_item(item)
        if len(selected) >= limit:
            break

    return selected[:limit]


def _read_markdown_preview(path: Path) -> Dict[str, Any]:
    if not path.exists() or path.suffix.lower() != ".md":
        return {"available": path.exists(), "text": "", "headings": []}

    text = path.read_text(encoding="utf-8", errors="replace")
    headings = [
        line.strip()
        for line in text.splitlines()
        if line.lstrip().startswith("#")
    ][:20]
    return {"available": True, "text": text[:8000], "headings": headings}


def build_dry_run_result(item: Dict[str, Any], manifest_path: Path) -> Dict[str, Any]:
    path_text = item.get("file_path", "")
    path = Path(path_text)
    preview = _read_markdown_preview(path)
    return {
        "parser": "dry-run",
        "source_file": _display_name(path_text),
        "original_path": path_text,
        "status": item.get("status", "unknown"),
        "document_type": _document_type(path_text),
        "manifest_metadata": {
            "asset_type": item.get("asset_type", ""),
            "confidence": item.get("confidence", ""),
            "tags": item.get("tags", []),
            "reason": item.get("reason", ""),
            "expected_usage": item.get("expected_usage", ""),
            "metadata_source": str(manifest_path),
        },
        "source_available": preview["available"],
        "content": {
            "text": preview["text"],
            "headings": preview["headings"],
            "tables": [],
            "images": [],
        },
        "messages": (
            ["Source file was not available from this workspace; metadata-only dry-run record created."]
            if not preview["available"]
            else []
        ),
    }


def _load_docling_converter():
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except ImportError:
        return None
    return DocumentConverter


def build_real_docling_result(item: Dict[str, Any], manifest_path: Path) -> Dict[str, Any]:
    DocumentConverter = _load_docling_converter()
    if DocumentConverter is None:
        return {
            **build_dry_run_result(item, manifest_path),
            "parser": "docling-unavailable",
            "messages": [
                "Docling is not installed. Run in dry-run mode or install docling separately for real parsing."
            ],
        }

    path_text = item.get("file_path", "")
    path = Path(path_text)
    if not path.exists():
        result = build_dry_run_result(item, manifest_path)
        result["parser"] = "docling-skipped"
        result["messages"] = ["Source file is not available; Docling parse was skipped."]
        return result

    converter = DocumentConverter()
    converted = converter.convert(str(path))
    document = converted.document
    markdown_text = document.export_to_markdown()

    result = build_dry_run_result(item, manifest_path)
    result["parser"] = "docling"
    result["source_available"] = True
    result["content"]["text"] = markdown_text
    result["content"]["headings"] = [
        line.strip()
        for line in markdown_text.splitlines()
        if line.lstrip().startswith("#")
    ][:50]
    result["docling_metadata"] = {
        "export_format": "markdown",
        "note": "Raw Docling object is intentionally not persisted in this experiment.",
    }
    return result


def write_results(results: List[Dict[str, Any]], output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment": "docling_ingestion_eval",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def run(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    real: bool = False,
    limit: int = 6,
) -> Path:
    manifest_items = load_manifest(manifest_path)
    candidates = select_candidates(manifest_items, limit=limit)
    builder = build_real_docling_result if real else build_dry_run_result
    results = [builder(item, manifest_path) for item in candidates]
    return write_results(results, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run isolated Docling ingestion sample parse.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--limit", type=int, default=6)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Use standard-library metadata/text preview mode.")
    mode.add_argument("--real", action="store_true", help="Try real Docling parsing if docling is installed.")
    args = parser.parse_args()

    output_path = run(
        manifest_path=args.manifest,
        output_path=args.output,
        real=args.real,
        limit=args.limit,
    )
    if args.real and _load_docling_converter() is None:
        print("Docling is not installed. Wrote docling-unavailable records instead of failing.")
    print(f"Wrote parse results: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
