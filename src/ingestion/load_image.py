"""Image loader placeholder.

PNG/JPG support is intentionally reserved for a later step.
Future behavior may include OCR, image captioning, or manual tagging.
"""

from pathlib import Path


def load_image(path: Path) -> dict:
    """Load an image file.

    Reserved interface. Real image parsing will be implemented later.
    """
    raise NotImplementedError("Image loading is reserved for a later phase.")

