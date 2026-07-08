"""TXT loader placeholder.

First-version responsibility:
- read plain text narrative notes
- preserve source path
- return text plus lightweight source metadata
"""

from pathlib import Path


def load_txt(path: Path) -> dict:
    """Load a TXT file as raw text plus source metadata."""
    text = path.read_text(encoding="utf-8-sig")
    return {
        "text": text,
        "source_path": str(path),
        "file_name": path.name,
        "file_type": "txt",
    }
