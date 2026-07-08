"""Markdown loader placeholder.

First-version responsibility:
- read Markdown files from knowledge_base/raw_assets
- preserve source path and title-like heading information
- return plain text plus lightweight source metadata
"""

from pathlib import Path


def load_markdown(path: Path) -> dict:
    """Load a Markdown file as raw text plus source metadata."""
    text = path.read_text(encoding="utf-8-sig")
    return {
        "text": text,
        "source_path": str(path),
        "file_name": path.name,
        "file_type": "markdown",
    }
