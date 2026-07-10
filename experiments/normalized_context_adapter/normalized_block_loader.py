"""Load normalized ingestion blocks for the adapter experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLOCKS_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "docling_ingestion_eval"
    / "sample_outputs"
    / "normalized_blocks.jsonl"
)


class NormalizedBlocksMissingError(FileNotFoundError):
    """Raised when the normalized blocks file has not been generated yet."""


def missing_blocks_message(path: Path = DEFAULT_BLOCKS_PATH) -> str:
    return (
        f"Normalized blocks file not found: {path}\n"
        "Run the ingestion dry-run first:\n"
        "E:\\Desktop\\python310\\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --dry-run\n"
        "E:\\Desktop\\python310\\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py"
    )


def load_normalized_blocks(path: Path = DEFAULT_BLOCKS_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        raise NormalizedBlocksMissingError(missing_blocks_message(path))
    blocks: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            blocks.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description="Load normalized blocks for the adapter experiment.")
    parser.add_argument("--blocks", type=Path, default=DEFAULT_BLOCKS_PATH)
    args = parser.parse_args()
    try:
        blocks = load_normalized_blocks(args.blocks)
    except NormalizedBlocksMissingError as exc:
        print(str(exc))
        return 1
    print(f"Loaded {len(blocks)} normalized blocks from {args.blocks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
