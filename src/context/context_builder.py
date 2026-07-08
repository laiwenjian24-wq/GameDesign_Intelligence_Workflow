"""Narrative Context Pack builder.

This module sits between retrieval and later workflow steps such as
continuity_checker or scene_writer. It is rule-based and does not call an LLM.
"""

from pathlib import Path
from typing import Dict, List

from src.context.context_schema import citation_from_result, empty_context_pack
from src.retrieval.query import query_knowledge_base
from src.retrieval.status_priority import get_usage_rule, group_sources_by_status


def _restriction_for_status(status: str) -> str:
    """Return a human-readable restriction for a source status."""
    return f"{status}: {get_usage_rule(status)}"


def _build_missing_evidence(task: str, grouped: Dict[str, List[Dict]]) -> List[str]:
    """Build missing evidence warnings for the context pack."""
    missing = []

    if not grouped.get("canon"):
        missing.append("No canon source retrieved. Do not make factual continuity decisions without human review.")

    if grouped.get("unknown"):
        missing.append("Unknown-status sources were retrieved. Treat them as unverified and require human confirmation.")

    if ("安全屋" in task or "safehouse" in task.lower()) and not any(
        "safehouse" in source.get("excerpt", "").lower()
        or "安全屋" in source.get("excerpt", "")
        for source in grouped.get("canon", [])
    ):
        missing.append("Task mentions safehouse, but no safehouse canon excerpt was retrieved.")

    return missing


def build_context_pack(task: str, index_dir: Path, top_k: int = 5) -> Dict:
    """Build a structured Narrative Context Pack from retrieval results."""
    retrieval_results = query_knowledge_base(task, index_dir, top_k=top_k)
    grouped = group_sources_by_status(retrieval_results)
    context_pack = empty_context_pack(task)

    context_pack["canon_context"] = [
        citation_from_result(result) for result in grouped.get("canon", [])
    ]
    context_pack["draft_reference"] = [
        citation_from_result(result) for result in grouped.get("draft", [])
    ]
    context_pack["pattern_context"] = [
        citation_from_result(result) for result in grouped.get("pattern", [])
    ]
    context_pack["inspiration_context"] = [
        citation_from_result(result) for result in grouped.get("inspiration", [])
    ]
    context_pack["deprecated_warnings"] = [
        citation_from_result(result) for result in grouped.get("deprecated", [])
    ]
    context_pack["unverified_context"] = [
        citation_from_result(result) for result in grouped.get("unknown", [])
    ]
    context_pack["missing_evidence"] = _build_missing_evidence(task, grouped)
    context_pack["restrictions"] = [
        _restriction_for_status("canon"),
        _restriction_for_status("draft"),
        _restriction_for_status("pattern"),
        _restriction_for_status("inspiration"),
        _restriction_for_status("deprecated"),
        _restriction_for_status("unknown"),
    ]
    context_pack["evidence_sources"] = [
        citation_from_result(result) for result in retrieval_results
    ]

    return context_pack


def _append_citations(lines: List[str], citations: List[Dict]) -> None:
    """Append citation entries to Markdown output."""
    if not citations:
        lines.append("- 无")
        return

    for citation in citations:
        lines.append(f"- {citation.get('source_file', '')} [{citation.get('status', 'unknown')}]")
        if citation.get("summary"):
            lines.append(f"  - summary: {citation.get('summary', '')}")
        lines.append(f"  - excerpt: {citation.get('excerpt', '')}")
        lines.append(f"  - reason_used: {citation.get('reason_used', '')}")


def format_context_pack_markdown(context_pack: Dict) -> str:
    """Format a Narrative Context Pack as Markdown."""
    task_context = context_pack.get("task_context", {})
    project_context = context_pack.get("project_context", {})

    lines = [
        "# Narrative Context Pack",
        "",
        "## 1. task_context",
        f"- task: {task_context.get('task', '')}",
        f"- task_type: {task_context.get('task_type', '')}",
        "",
        "## 2. project_context",
        f"- project: {project_context.get('project', '')}",
        f"- workflow_stage: {project_context.get('workflow_stage', '')}",
        "",
        "## 3. canon_context",
    ]

    _append_citations(lines, context_pack.get("canon_context", []))

    lines.extend(["", "## 4. draft_reference"])
    _append_citations(lines, context_pack.get("draft_reference", []))

    lines.extend(["", "## 5. pattern_context"])
    _append_citations(lines, context_pack.get("pattern_context", []))

    lines.extend(["", "## 6. inspiration_context"])
    _append_citations(lines, context_pack.get("inspiration_context", []))

    lines.extend(["", "## 7. deprecated_warnings"])
    _append_citations(lines, context_pack.get("deprecated_warnings", []))

    lines.extend(["", "## 8. missing_evidence"])
    missing = context_pack.get("missing_evidence", [])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")

    unverified = context_pack.get("unverified_context", [])
    if unverified:
        lines.extend(["", "### unverified_context"])
        _append_citations(lines, unverified)

    lines.extend(["", "## 9. restrictions"])
    for restriction in context_pack.get("restrictions", []):
        lines.append(f"- {restriction}")

    lines.extend(["", "## 10. evidence_sources"])
    _append_citations(lines, context_pack.get("evidence_sources", []))

    return "\n".join(lines)

