"""LLM-assisted evidence selection for Context Pack construction."""

from typing import Dict, List, Tuple

from src.llm.client import parse_json_object_from_content
from src.llm.schemas import EvidenceSelection, RetrievalPlan
from src.rag.evidence_snippet import refine_evidence_excerpt


def _selection_from_payload(payload: Dict) -> EvidenceSelection:
    """Build an EvidenceSelection with conservative defaults."""
    return EvidenceSelection(
        selected_canon=list(payload.get("selected_canon", [])),
        selected_draft=list(payload.get("selected_draft", [])),
        selected_deprecated=list(payload.get("selected_deprecated", [])),
        selected_inspiration=list(payload.get("selected_inspiration", [])),
        rejected=list(payload.get("rejected", [])),
        warnings=list(payload.get("warnings", [])),
        missing_evidence=list(payload.get("missing_evidence", [])),
    )


def _candidate_id(index: int) -> str:
    """Return a stable candidate id for one selection request."""
    return f"c{index:03d}"


def _prepare_candidates(candidates: List[Dict]) -> Tuple[List[Dict], Dict[str, Dict]]:
    """Assign ids and produce compact candidates for the LLM."""
    compact_candidates = []
    candidate_map = {}
    for index, candidate in enumerate(candidates, start=1):
        candidate_id = candidate.get("candidate_id") or _candidate_id(index)
        full_candidate = dict(candidate)
        full_candidate["candidate_id"] = candidate_id
        candidate_map[candidate_id] = full_candidate

        metadata = candidate.get("metadata", {})
        compact_candidates.append(
            {
                "candidate_id": candidate_id,
                "source_file": candidate.get("source_file", ""),
                "status": candidate.get("status", "unknown"),
                "heading": metadata.get("heading", ""),
                "section_title": metadata.get("section_title", ""),
                "excerpt": candidate.get("excerpt", ""),
                "score": candidate.get("score", 0),
            }
        )
    return compact_candidates, candidate_map


def _ids(payload: Dict, key: str) -> List[str]:
    """Return a list of ids from a payload key."""
    return [str(item) for item in payload.get(key, [])]


def _items_for_ids(
    selected_ids: List[str],
    candidate_map: Dict[str, Dict],
    expected_status: str,
    warnings: List[str],
) -> List[Dict]:
    """Map selected ids back to full candidates without changing status."""
    items = []
    for candidate_id in selected_ids:
        candidate = candidate_map.get(candidate_id)
        if candidate is None:
            warnings.append(f"unknown candidate_id ignored: {candidate_id}")
            continue
        if candidate.get("status") != expected_status:
            warnings.append(
                f"candidate_id {candidate_id} has status {candidate.get('status')} "
                f"and cannot be selected as {expected_status}"
            )
            continue
        items.append(dict(candidate))
    return items


def _refine_items(items: List[Dict], retrieval_plan: RetrievalPlan) -> List[Dict]:
    """Refine evidence excerpts without changing source status or full text."""
    refined = []
    for item in items:
        enriched = dict(item)
        enriched["excerpt"] = refine_evidence_excerpt(enriched, retrieval_plan)
        refined.append(enriched)
    return refined


def select_evidence_for_context_pack(
    question: str,
    retrieval_plan: RetrievalPlan,
    candidates: List[Dict],
    llm_client,
) -> EvidenceSelection:
    """Select evidence from candidates without changing source status."""
    compact_candidates, candidate_map = _prepare_candidates(candidates)
    response = llm_client.complete(
        "Select evidence for a Context Pack without changing source status.",
        context={
            "task": "evidence_selection",
            "question": question,
            "retrieval_plan": retrieval_plan.to_dict(),
            "candidates": compact_candidates,
        },
    )
    payload = parse_json_object_from_content(response.text)

    warnings = list(payload.get("warnings", []))
    selection = EvidenceSelection(
        selected_canon=_items_for_ids(
            _ids(payload, "selected_canon_ids"),
            candidate_map,
            "canon",
            warnings,
        ),
        selected_draft=_items_for_ids(
            _ids(payload, "selected_draft_ids"),
            candidate_map,
            "draft",
            warnings,
        ),
        selected_deprecated=_items_for_ids(
            _ids(payload, "selected_deprecated_ids"),
            candidate_map,
            "deprecated",
            warnings,
        ),
        selected_inspiration=_items_for_ids(
            _ids(payload, "selected_inspiration_ids"),
            candidate_map,
            "inspiration",
            warnings,
        ),
        rejected=[
            {
                "candidate_id": candidate_id,
                "source_file": candidate_map.get(candidate_id, {}).get("source_file", ""),
                "status": candidate_map.get(candidate_id, {}).get("status", "unknown"),
                "reason": "Rejected by evidence selector.",
            }
            for candidate_id in _ids(payload, "rejected_ids")
            if candidate_id in candidate_map
        ],
        warnings=warnings,
        missing_evidence=list(payload.get("missing_evidence", [])),
    )

    selection.selected_canon = _refine_items(selection.selected_canon, retrieval_plan)
    selection.selected_draft = _refine_items(selection.selected_draft, retrieval_plan)
    selection.selected_deprecated = _refine_items(
        selection.selected_deprecated,
        retrieval_plan,
    )
    selection.selected_inspiration = _refine_items(
        selection.selected_inspiration,
        retrieval_plan,
    )

    if not selection.selected_canon:
        if "insufficient canon evidence" not in selection.warnings:
            selection.warnings.append("insufficient canon evidence")
        if "no canon evidence selected" not in selection.missing_evidence:
            selection.missing_evidence.append("no canon evidence selected")
    return selection
