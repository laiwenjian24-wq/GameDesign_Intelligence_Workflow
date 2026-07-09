"""Build the experimental LlamaIndex node store from the import manifest."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from src.rag.node_metadata import ensure_node_metadata, metadata_from_manifest_item


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "knowledge_base" / "import_manifest.json"
DEFAULT_LLAMA_INDEX_DIR = PROJECT_ROOT / "knowledge_base" / "llama_index"
NODES_FILENAME = "nodes.json"


try:
    from llama_index.core import Document as LlamaDocument
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.schema import TextNode
except ImportError:  # pragma: no cover - exercised in environments without deps.
    LlamaDocument = None
    SentenceSplitter = None
    TextNode = None


@dataclass
class SimpleDocument:
    """Small fallback document shape matching the LlamaIndex fields we use."""

    text: str
    metadata: Dict


@dataclass
class SimpleNode:
    """Small fallback node shape matching the LlamaIndex fields we use."""

    text: str
    metadata: Dict

    def get_content(self) -> str:
        """Return node text using the same accessor name as LlamaIndex nodes."""
        return self.text


def _read_manifest(manifest_path: Path) -> List[Dict]:
    """Read the import manifest."""
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _read_source_text(file_path: str) -> str:
    """Read one source file from the manifest."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig")


def _document(text: str, metadata: Dict):
    """Create a LlamaIndex Document when available, otherwise a fallback."""
    if LlamaDocument is not None:
        return LlamaDocument(text=text, metadata=metadata)
    return SimpleDocument(text=text, metadata=metadata)


def _document_text(document) -> str:
    """Return text from a LlamaIndex or fallback document."""
    return getattr(document, "text", "") or getattr(document, "text_resource", "")


def _node_text(node) -> str:
    """Return text from a LlamaIndex or fallback node."""
    if hasattr(node, "get_content"):
        return node.get_content()
    return getattr(node, "text", "")


def create_documents_from_manifest(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> List:
    """Load manifest sources as LlamaIndex Documents with governance metadata."""
    manifest_items = _read_manifest(manifest_path)
    documents = []

    for item in manifest_items:
        text = _read_source_text(item.get("file_path", ""))
        if not text.strip():
            continue

        metadata = metadata_from_manifest_item(item, str(manifest_path))
        documents.append(_document(text=text, metadata=metadata))

    return documents


def _fallback_markdown_chunks(text: str, chunk_size: int) -> List[str]:
    """Split Markdown with heading awareness, then cap oversized chunks."""
    sections = re.split(r"(?m)(?=^#{1,6}\s+)", text)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= chunk_size:
            chunks.append(section)
            continue

        paragraphs = re.split(r"\n\s*\n", section)
        current = ""
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if current and len(current) + len(paragraph) + 2 > chunk_size:
                chunks.append(current)
                current = paragraph
            else:
                current = paragraph if not current else f"{current}\n\n{paragraph}"
        if current:
            chunks.append(current)

    return chunks


def parse_documents_to_nodes(
    documents: Iterable,
    chunk_size: int = 800,
    chunk_overlap: int = 80,
) -> List:
    """Parse documents into nodes while preserving source metadata."""
    documents = list(documents)
    if is_real_llamaindex_available():
        splitter = SentenceSplitter.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.get_nodes_from_documents(documents)

    nodes = []
    for document in documents:
        metadata = ensure_node_metadata(getattr(document, "metadata", {}))
        for chunk in _fallback_markdown_chunks(_document_text(document), chunk_size):
            nodes.append(SimpleNode(text=chunk, metadata=dict(metadata)))
    return nodes


def serialize_node(node) -> Dict:
    """Serialize one LlamaIndex or fallback node for local persistence."""
    metadata = ensure_node_metadata(getattr(node, "metadata", {}))
    return {
        "text": _node_text(node),
        "metadata": metadata,
    }


def is_real_llamaindex_available() -> bool:
    """Return whether LlamaIndex document and node parsing APIs are available."""
    return LlamaDocument is not None and SentenceSplitter is not None


def node_from_serialized(item: Dict):
    """Rebuild a LlamaIndex TextNode from serialized node data when available."""
    metadata = ensure_node_metadata(item.get("metadata", {}))
    text = item.get("text", "")
    if TextNode is None:
        return SimpleNode(text=text, metadata=metadata)
    return TextNode(text=text, metadata=metadata)


def build_llamaindex_nodes(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    index_dir: Path = DEFAULT_LLAMA_INDEX_DIR,
    chunk_size: int = 800,
    chunk_overlap: int = 80,
) -> List[Dict]:
    """Build and persist the experimental LlamaIndex node store."""
    documents = create_documents_from_manifest(manifest_path)
    nodes = parse_documents_to_nodes(
        documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    serialized = [serialize_node(node) for node in nodes if _node_text(node).strip()]

    index_dir.mkdir(parents=True, exist_ok=True)
    output_path = index_dir / NODES_FILENAME
    output_path.write_text(
        json.dumps(serialized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return serialized


def load_llamaindex_nodes(index_dir: Path = DEFAULT_LLAMA_INDEX_DIR) -> List[Dict]:
    """Load persisted experimental LlamaIndex nodes."""
    path = index_dir / NODES_FILENAME
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
