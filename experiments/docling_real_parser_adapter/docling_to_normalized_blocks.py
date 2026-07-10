"""Convert Docling parse summaries into v1 NormalizedBlock JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.v1.ingestion.normalized_block import NormalizedBlock  # noqa: E402
from src.v1.ingestion.status_policy import normalize_status  # noqa: E402


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_PATH = EXPERIMENT_DIR / "sample_outputs" / "docling_parse_summary.json"
DEFAULT_OUTPUT_PATH = EXPERIMENT_DIR / "sample_outputs" / "real_docling_normalized_blocks.jsonl"


def _slug(text: str) -> str:
    cleaned = re.sub(r"\s+", "-", str(text).strip())
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_.-]+", "", cleaned)
    return cleaned[:80] or "untitled"


def _looks_like_table(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pipe_lines = [line for line in lines if "|" in line]
    return len(pipe_lines) >= 2 and any("---" in line for line in pipe_lines)


def _split_markdown(markdown: str) -> List[Dict[str, Any]]:
    if not markdown.strip():
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
        text = "\n".join(buffer).strip()
        if not text:
            buffer = []
            return
        blocks.append(
            {
                "section_title": section_title,
                "heading_path": list(heading_stack),
                "block_type": "table" if _looks_like_table(text) else "text",
                "text": text,
                "page_number": None,
            }
        )
        buffer = []

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip() or "Untitled"
            heading_stack = heading_stack[: max(level - 1, 0)]
            heading_stack.append(title)
            section_title = title
            continue
        if not stripped:
            flush()
            continue
        buffer.append(line)
    flush()
    return blocks


def _metadata_for_result(result: Dict[str, Any], block: Dict[str, Any]) -> Dict[str, Any]:
    content = result.get("content", {}) or {}
    metadata = {
        **(result.get("manifest_metadata", {}) or {}),
        "parser": result.get("parser", "unknown"),
        "source_available": result.get("source_available", False),
        "messages": result.get("messages", []),
    }
    if not block.get("heading_path"):
        metadata["missing_heading_info"] = True
    if block.get("page_number") is None:
        metadata["missing_page_number"] = True
    if not content.get("tables"):
        metadata["missing_table_info"] = True
    if not content.get("images"):
        metadata["missing_image_info"] = True
    return metadata


def normalize_docling_result(result: Dict[str, Any]) -> List[NormalizedBlock]:
    content = result.get("content", {}) or {}
    markdown = content.get("markdown", "") or content.get("text", "") or ""
    blocks = _split_markdown(markdown)
    normalized: List[NormalizedBlock] = []
    source_file = result.get("source_file") or Path(result.get("original_path", "")).name
    status = normalize_status(result.get("status", "unknown"))
    for index, block in enumerate(blocks, start=1):
        normalized.append(
            NormalizedBlock(
                block_id=f"{_slug(source_file)}::{index:04d}",
                source_file=source_file,
                original_path=result.get("original_path", ""),
                status=status,
                document_type=result.get("document_type", "unknown"),
                section_title=block.get("section_title", "Metadata only"),
                heading_path=list(block.get("heading_path", [])),
                page_number=block.get("page_number"),
                block_type=block.get("block_type", "unknown"),
                text=block.get("text", ""),
                metadata=_metadata_for_result(result, block),
            )
        )
    return normalized


def normalize_summary_payload(payload: Dict[str, Any]) -> List[NormalizedBlock]:
    blocks: List[NormalizedBlock] = []
    for result in payload.get("results", []):
        blocks.extend(normalize_docling_result(result))
    return blocks


def write_jsonl(blocks: Iterable[NormalizedBlock], output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(block.to_dict(), ensure_ascii=False) for block in blocks]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return output_path


def run(input_path: Path = DEFAULT_INPUT_PATH, output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    blocks = normalize_summary_payload(payload)
    return write_jsonl(blocks, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Docling parse summary to v1 NormalizedBlock JSONL.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    if not args.input.exists():
        print(f"Docling parse summary not found: {args.input}")
        print("Run docling_real_parse.py first.")
        return 1
    output_path = run(args.input, args.output)
    print(f"Wrote real Docling normalized blocks: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
