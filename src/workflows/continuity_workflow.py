"""Backward-compatible wrapper for the continuity checker."""

from pathlib import Path

from src.workflows.continuity_checker import run_continuity_check as _run_check


def run_continuity_check(draft_text: str, index_dir: Path) -> dict:
    """Check a draft scene or plot note against local indexed materials."""
    return _run_check(draft_text, index_dir)
