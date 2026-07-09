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


def _node(text: str, metadata: Dict):
    """Create a LlamaIndex TextNode when available, otherwise a fallback node."""
    metadata = ensure_node_metadata(metadata)
    if TextNode is not None:
        return TextNode(text=text, metadata=metadata)
    return SimpleNode(text=text, metadata=metadata)


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


def _markdown_sections(text: str) -> List[Dict]:
    """Split Markdown into heading-aware sections with heading metadata."""
    sections = []
    heading_stack: List[tuple] = []
    current_lines: List[str] = []
    current_heading = ""
    current_path: List[str] = []

    def flush_current() -> None:
        body = "\n".join(current_lines).strip()
        if not body:
            return
        sections.append(
            {
                "text": body,
                "heading": current_heading,
                "heading_path": list(current_path),
                "section_title": current_heading,
            }
        )

    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            flush_current()
            level = len(match.group(1))
            title = match.group(2).strip()
            heading_stack = [
                (existing_level, existing_title)
                for existing_level, existing_title in heading_stack
                if existing_level < level
            ]
            heading_stack.append((level, title))
            current_heading = title
            current_path = [title for _, title in heading_stack]
            current_lines = [line]
            continue

        current_lines.append(line)

    flush_current()
    if not sections and text.strip():
        return [
            {
                "text": text.strip(),
                "heading": "",
                "heading_path": [],
                "section_title": "",
            }
        ]
    return sections


def _chunk_section(section: Dict, chunk_size: int) -> List[Dict]:
    """Cap oversized Markdown sections without dropping heading metadata."""
    text = section.get("text", "").strip()
    if len(text) <= chunk_size:
        return [section]

    chunks = []
    paragraphs = re.split(r"\n\s*\n", text)
    current = ""
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if current and len(current) + len(paragraph) + 2 > chunk_size:
            chunk = dict(section)
            chunk["text"] = current
            chunks.append(chunk)
            current = paragraph
        else:
            current = paragraph if not current else f"{current}\n\n{paragraph}"
    if current:
        chunk = dict(section)
        chunk["text"] = current
        chunks.append(chunk)

    return chunks


def _is_markdown_document(document) -> bool:
    """Return whether a document came from a Markdown source."""
    metadata = getattr(document, "metadata", {}) or {}
    path = metadata.get("file_path") or metadata.get("source_file", "")
    return str(path).lower().endswith((".md", ".markdown"))


def _section_nodes_from_document(document, chunk_size: int) -> List:
    """Build heading-aware nodes from one Markdown document."""
    base_metadata = ensure_node_metadata(getattr(document, "metadata", {}))
    nodes = []
    for section in _markdown_sections(_document_text(document)):
        for chunk in _chunk_section(section, chunk_size):
            metadata = dict(base_metadata)
            metadata["heading"] = chunk.get("heading", "")
            metadata["heading_path"] = chunk.get("heading_path", [])
            metadata["section_title"] = chunk.get("section_title", "")
            nodes.append(_node(chunk.get("text", ""), metadata))
    return nodes


def parse_documents_to_nodes(
    documents: Iterable,
    chunk_size: int = 800,
    chunk_overlap: int = 80,
) -> List:
    """Parse documents into nodes while preserving source metadata."""
    documents = list(documents)
    markdown_nodes = []
    other_documents = []
    for document in documents:
        if _is_markdown_document(document):
            markdown_nodes.extend(_section_nodes_from_document(document, chunk_size))
        else:
            other_documents.append(document)

    if is_real_llamaindex_available():
        splitter = SentenceSplitter.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return markdown_nodes + splitter.get_nodes_from_documents(other_documents)

    nodes = list(markdown_nodes)
    for document in other_documents:
        metadata = ensure_node_metadata(getattr(document, "metadata", {}))
        for section in _markdown_sections(_document_text(document)):
            for chunk in _chunk_section(section, chunk_size):
                nodes.append(_node(chunk.get("text", ""), dict(metadata)))
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
