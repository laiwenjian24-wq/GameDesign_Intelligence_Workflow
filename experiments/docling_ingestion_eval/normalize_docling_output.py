"""Normalize Docling or dry-run parse results into status-aware blocks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_PATH = EXPERIMENT_DIR / "sample_outputs" / "docling_parse_results.json"
DEFAULT_OUTPUT_PATH = EXPERIMENT_DIR / "sample_outputs" / "normalized_blocks.jsonl"


def _slug(text: str) -> str:
    cleaned = re.sub(r"\s+", "-", text.strip())
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_.-]+", "", cleaned)
    return cleaned[:80] or "untitled"


def _heading_level(line: str) -> int:
    return len(line) - len(line.lstrip("#"))


def _split_markdown_blocks(text: str) -> List[Dict[str, Any]]:
    if not text.strip():
        return [
            {
                "section_title": "Metadata only",
                "heading_path": [],
                "block_type": "unknown",
                "text": "",
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
        block_type = "table" if _looks_like_table(content) else "text"
        blocks.append(
            {
                "section_title": section_title,
                "heading_path": list(heading_stack),
                "block_type": block_type,
                "text": content,
            }
        )
        buffer = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            level = _heading_level(stripped)
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


def _looks_like_table(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    pipe_lines = [line for line in lines if "|" in line]
    return len(pipe_lines) >= 2 and any("---" in line for line in pipe_lines)


def normalize_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    content = result.get("content", {})
    text = content.get("text", "") or ""
    metadata = {
        **result.get("manifest_metadata", {}),
        "parser": result.get("parser", "unknown"),
        "source_available": result.get("source_available", False),
        "messages": result.get("messages", []),
    }
    blocks = _split_markdown_blocks(text)
    normalized: List[Dict[str, Any]] = []
    source_file = result.get("source_file", "")
    for index, block in enumerate(blocks, start=1):
        section_title = block.get("section_title", "Metadata only")
        normalized.append(
            {
                "block_id": f"{_slug(source_file)}::{index:04d}",
                "source_file": source_file,
                "original_path": result.get("original_path", ""),
                "status": result.get("status", "unknown"),
                "document_type": result.get("document_type", "unknown"),
                "section_title": section_title,
                "heading_path": block.get("heading_path", []),
                "page_number": block.get("page_number"),
                "block_type": block.get("block_type", "unknown"),
                "text": block.get("text", ""),
                "metadata": metadata,
            }
        )
    return normalized


def normalize_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for result in payload.get("results", []):
        normalized.extend(normalize_result(result))
    return normalized


def write_jsonl(blocks: Iterable[Dict[str, Any]], output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(block, ensure_ascii=False) for block in blocks]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return output_path


def run(input_path: Path = DEFAULT_INPUT_PATH, output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    blocks = normalize_payload(payload)
    return write_jsonl(blocks, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Docling ingestion sample output.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    output_path = run(args.input, args.output)
    print(f"Wrote normalized blocks: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
