"""Keyword index builder for the first retrieval MVP.

This is intentionally not an embedding index yet. It reads metadata records,
loads the original text files, and writes a simple local JSON index that can be
queried with keyword matching.
"""

import json
from pathlib import Path
from typing import Dict, List


def _read_jsonl(path: Path) -> List[Dict]:
    """Read JSONL records from disk."""
    if not path.exists():
        return []

    records = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _read_source_text(file_path: str) -> str:
    """Read the raw source text referenced by a metadata record."""
    path = Path(file_path)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig")


def build_index(processed_dir: Path, index_dir: Path) -> List[Dict]:
    """Build a local keyword index from metadata and raw source text."""
    metadata_path = processed_dir / "metadata.jsonl"
    records = _read_jsonl(metadata_path)

    index_records = []
    for record in records:
        text = _read_source_text(record.get("file_path", ""))
        searchable_text = " ".join(
            [
                record.get("filename", ""),
                record.get("status", ""),
                record.get("summary", ""),
                " ".join(record.get("related_characters", [])),
                " ".join(record.get("related_locations", [])),
                " ".join(record.get("related_branches", [])),
                " ".join(record.get("tags", [])),
                text,
            ]
        )

        index_records.append(
            {
                "metadata": record,
                "text": text,
                "searchable_text": searchable_text.lower(),
            }
        )

    index_dir.mkdir(parents=True, exist_ok=True)
    output_path = index_dir / "keyword_index.json"
    output_path.write_text(
        json.dumps(index_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return index_records
