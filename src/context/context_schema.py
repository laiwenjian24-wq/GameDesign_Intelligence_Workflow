"""Schema helpers for Narrative Context Pack.

The first version uses plain dictionaries to keep the project lightweight and
compatible with the current Python environment.
"""

from typing import Dict, List


CONTEXT_PACK_SECTIONS = [
    "task_context",
    "project_context",
    "canon_context",
    "draft_reference",
    "pattern_context",
    "inspiration_context",
    "deprecated_warnings",
    "missing_evidence",
    "restrictions",
    "evidence_sources",
]


def empty_context_pack(task: str) -> Dict:
    """Create an empty Narrative Context Pack shape."""
    return {
        "task_context": {
            "task": task,
            "task_type": "continuity_or_scene_context",
        },
        "project_context": {
            "project": "STUPID",
            "workflow_stage": "Narrative Workflow MVP",
        },
        "canon_context": [],
        "draft_reference": [],
        "pattern_context": [],
        "inspiration_context": [],
        "deprecated_warnings": [],
        "unverified_context": [],
        "missing_evidence": [],
        "restrictions": [],
        "evidence_sources": [],
    }


def citation_from_result(result: Dict) -> Dict:
    """Normalize a retrieval result into a source citation."""
    return {
        "source_file": result.get("source_file") or result.get("filename", ""),
        "status": result.get("status", "unknown"),
        "summary": result.get("summary", ""),
        "excerpt": result.get("excerpt") or result.get("relevant_excerpt", ""),
        "reason_used": result.get("reason_used", ""),
    }


def has_sources(items: List[Dict]) -> bool:
    """Return whether a context section has cited sources."""
    return bool(items)

