"""Build a full-context bundle for manual RAG baseline comparison."""

import json
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "knowledge_base" / "import_manifest.json"

STATUS_SECTIONS = {
    "canon": "Canon Documents",
    "draft": "Draft Reference",
    "deprecated": "Deprecated Warnings",
    "inspiration": "Inspiration Reference",
}

LLM_INSTRUCTIONS = [
    "Canon is the only authoritative fact source.",
    "Draft can be used only as writing reference and must not override Canon.",
    "Deprecated can be used only as historical conflict evidence and must not be treated as current fact.",
    "Inspiration can be used only as thematic reference and must not be treated as fact.",
    "If Canon does not contain enough evidence, answer that evidence is insufficient.",
    "Every answer must list the source files used.",
]


def _read_manifest(manifest_path: Path) -> List[Dict]:
    """Read the import manifest without modifying it."""
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _read_source_text(file_path: str) -> str:
    """Read one source document from the manifest."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig")


def _empty_groups() -> Dict[str, List[Dict]]:
    """Create the supported status groups for the bundle."""
    return {status: [] for status in STATUS_SECTIONS}


def _rough_token_estimate(character_count: int) -> int:
    """Return a rough, provider-neutral token estimate."""
    if character_count <= 0:
        return 0
    return max(1, round(character_count / 3))


def build_full_context_bundle(
    question: str,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> Dict:
    """Build a full-context bundle from all manifest sources grouped by status."""
    manifest_items = _read_manifest(manifest_path)
    grouped = _empty_groups()
    source_list = []
    total_characters = 0

    for item in manifest_items:
        status = str(item.get("status", "unknown")).lower()
        if status not in grouped:
            continue

        file_path = item.get("file_path", "")
        text = _read_source_text(file_path)
        document = {
            "source_file": file_path,
            "status": status,
            "asset_type": item.get("asset_type", ""),
            "tags": item.get("tags", []),
            "reason": item.get("reason", ""),
            "expected_usage": item.get("expected_usage", ""),
            "text": text,
            "character_count": len(text),
        }
        grouped[status].append(document)
        source_list.append(
            {
                "source_file": file_path,
                "status": status,
                "asset_type": item.get("asset_type", ""),
                "character_count": len(text),
            }
        )
        total_characters += len(text)

    return {
        "question": question,
        "instructions": list(LLM_INSTRUCTIONS),
        "groups": grouped,
        "source_list": source_list,
        "estimated_character_count": total_characters,
        "rough_token_estimate": _rough_token_estimate(total_characters),
    }


def _format_document(document: Dict) -> List[str]:
    """Format one source document for Markdown output."""
    lines = [
        f"### {document.get('source_file', '')}",
        "",
        f"- status: {document.get('status', '')}",
        f"- asset_type: {document.get('asset_type', '')}",
        f"- character_count: {document.get('character_count', 0)}",
    ]
    tags = document.get("tags", [])
    if tags:
        lines.append(f"- tags: {', '.join(str(tag) for tag in tags)}")
    if document.get("reason"):
        lines.append(f"- reason: {document.get('reason', '')}")
    if document.get("expected_usage"):
        lines.append(f"- expected_usage: {document.get('expected_usage', '')}")
    lines.extend(["", "```markdown", document.get("text", ""), "```", ""])
    return lines


def format_full_context_bundle_markdown(bundle: Dict) -> str:
    """Format a full-context bundle as Markdown for manual LLM comparison."""
    lines = [
        "# Full-context Bundle",
        "",
        "## Question",
        bundle.get("question", ""),
        "",
        "## Instructions for LLM",
    ]

    for instruction in bundle.get("instructions", []):
        lines.append(f"- {instruction}")

    lines.extend(
        [
            "",
            "## Source list",
        ]
    )
    for source in bundle.get("source_list", []):
        lines.append(
            f"- {source.get('source_file', '')} "
            f"[{source.get('status', '')}, {source.get('asset_type', '')}, "
            f"{source.get('character_count', 0)} chars]"
        )

    lines.extend(
        [
            "",
            "## Size Estimate",
            f"- Estimated character count: {bundle.get('estimated_character_count', 0)}",
            f"- Rough token estimate: {bundle.get('rough_token_estimate', 0)}",
            "",
        ]
    )

    groups = bundle.get("groups", {})
    for status, heading in STATUS_SECTIONS.items():
        lines.append(f"## {heading}")
        documents = groups.get(status, [])
        if not documents:
            lines.extend(["- None", ""])
            continue
        for document in documents:
            lines.extend(_format_document(document))

    return "\n".join(lines).rstrip() + "\n"
