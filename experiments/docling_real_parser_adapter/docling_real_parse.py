"""Run real Docling parsing when Docling is available.

The script degrades cleanly when Docling is not installed. It writes a compact
summary instead of persisting large raw parser objects.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "knowledge_base" / "import_manifest.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "sample_outputs"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "docling_parse_summary.json"
INSTALL_COMMAND = r"E:\Desktop\python310\python.exe -m pip install docling"
SUPPORTED_EXTENSIONS = {".md", ".docx", ".pdf", ".jpg", ".jpeg", ".png"}


def load_docling_converter():
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except ImportError:
        return None
    return DocumentConverter


def docling_available() -> bool:
    return load_docling_converter() is not None


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> List[Dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_manifest_samples(manifest_path: Path = DEFAULT_MANIFEST_PATH, limit: int = 3) -> List[Dict[str, Any]]:
    items = load_manifest(manifest_path)
    samples: List[Dict[str, Any]] = []
    for item in items:
        file_path = item.get("file_path", "")
        if Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS:
            samples.append(item)
        if len(samples) >= limit:
            break
    return samples


def _manifest_item_for_input(input_path: Path) -> Dict[str, Any]:
    return {
        "file_path": str(input_path),
        "status": "unknown",
        "asset_type": "manual_input",
        "tags": [],
        "confidence": "",
        "reason": "",
        "expected_usage": "",
    }


def _summary_from_unavailable(item: Dict[str, Any], message: str) -> Dict[str, Any]:
    file_path = item.get("file_path", "")
    return {
        "parser": "docling_not_installed",
        "source_file": Path(file_path).name,
        "original_path": file_path,
        "status": item.get("status", "unknown"),
        "document_type": Path(file_path).suffix.lower().lstrip(".") or "unknown",
        "source_available": Path(file_path).exists(),
        "content": {
            "markdown": "",
            "headings": [],
            "tables": [],
            "images": [],
            "pages": [],
        },
        "manifest_metadata": {
            "asset_type": item.get("asset_type", ""),
            "confidence": item.get("confidence", ""),
            "tags": item.get("tags", []),
            "reason": item.get("reason", ""),
            "expected_usage": item.get("expected_usage", ""),
        },
        "messages": [message, f"Install with: {INSTALL_COMMAND}"],
    }


def parse_one_item(item: Dict[str, Any], converter_cls: Optional[Any]) -> Dict[str, Any]:
    file_path = item.get("file_path", "")
    path = Path(file_path)
    if converter_cls is None:
        return _summary_from_unavailable(item, "docling_not_installed")
    if not path.exists():
        result = _summary_from_unavailable(item, "source_file_not_found")
        result["parser"] = "docling_skipped"
        return result

    converter = converter_cls()
    converted = converter.convert(str(path))
    document = converted.document
    markdown = document.export_to_markdown()
    headings = [line.strip() for line in markdown.splitlines() if line.lstrip().startswith("#")]

    return {
        "parser": "docling",
        "source_file": path.name,
        "original_path": str(path),
        "status": item.get("status", "unknown"),
        "document_type": path.suffix.lower().lstrip(".") or "unknown",
        "source_available": True,
        "content": {
            "markdown": markdown,
            "headings": headings,
            "tables": [],
            "images": [],
            "pages": [],
        },
        "manifest_metadata": {
            "asset_type": item.get("asset_type", ""),
            "confidence": item.get("confidence", ""),
            "tags": item.get("tags", []),
            "reason": item.get("reason", ""),
            "expected_usage": item.get("expected_usage", ""),
        },
        "messages": ["Docling parsed file and exported markdown. Raw parser object was not persisted."],
    }


def write_summary(results: Iterable[Dict[str, Any]], output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment": "docling_real_parser_adapter",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "docling_available": docling_available(),
        "install_command": INSTALL_COMMAND,
        "results": list(results),
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def run(
    input_path: Optional[Path] = None,
    from_manifest: bool = False,
    limit: int = 3,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> Path:
    if input_path is None and not from_manifest:
        raise ValueError("Provide --input or --from-manifest.")
    converter_cls = load_docling_converter()
    if input_path is not None:
        items = [_manifest_item_for_input(input_path)]
    else:
        items = select_manifest_samples(manifest_path, limit=limit)
    results = [parse_one_item(item, converter_cls) for item in items]
    return write_summary(results, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real Docling parse summary.")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--from-manifest", action="store_true")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    if not docling_available():
        print("docling_not_installed")
        print(f"Install with: {INSTALL_COMMAND}")

    try:
        output_path = run(
            input_path=args.input,
            from_manifest=args.from_manifest,
            limit=args.limit,
            output_path=args.output,
            manifest_path=args.manifest,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    print(f"Wrote Docling parse summary: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
