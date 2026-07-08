"""File scanning placeholder for narrative source assets."""

from pathlib import Path
from typing import List


SUPPORTED_FIRST_PASS_EXTENSIONS = {".md", ".txt"}
RESERVED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def scan_raw_assets(raw_assets_dir: Path) -> List[Path]:
    """Find Markdown and TXT source files for first-version ingestion.

    PDF and image extensions are intentionally reserved and ignored here.
    """
    if not raw_assets_dir.exists():
        return []

    return sorted(
        path
        for path in raw_assets_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_FIRST_PASS_EXTENSIONS
    )
