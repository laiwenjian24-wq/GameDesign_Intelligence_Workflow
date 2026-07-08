"""PDF loader placeholder.

PDF support is intentionally reserved for a later step.
The first MVP focuses on Markdown and TXT.
"""

from pathlib import Path


def load_pdf(path: Path) -> dict:
    """Load a PDF file.

    Reserved interface. Real PDF parsing will be implemented later.
    """
    raise NotImplementedError("PDF loading is reserved for a later phase.")

