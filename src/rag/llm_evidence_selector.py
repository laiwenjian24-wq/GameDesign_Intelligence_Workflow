"""LLM-assisted evidence selection for Context Pack construction."""

import json
from typing import Dict, List

from src.llm.schemas import EvidenceSelection, RetrievalPlan


def _selection_from_payload(payload: Dict) -> EvidenceSelection:
    """Build an EvidenceSelection with conservative defaults."""
    return EvidenceSelection(
        selected_canon=list(payload.get("selected_canon", [])),
        selected_draft=list(payload.get("selected_draft", [])),
        selected_deprecated=list(payload.get("selected_deprecated", [])),
        selected_inspiration=list(payload.get("selected_inspiration", [])),
        rejected=list(payload.get("rejected", [])),
        warnings=list(payload.get("warnings", [])),
    )


def select_evidence_for_context_pack(
    question: str,
    retrieval_plan: RetrievalPlan,
    candidates: List[Dict],
    llm_client,
) -> EvidenceSelection:
    """Select evidence from candidates without changing source status."""
    response = llm_client.complete(
        "Select evidence for a Context Pack without changing source status.",
        context={
            "task": "evidence_selection",
            "question": question,
            "retrieval_plan": retrieval_plan.to_dict(),
            "candidates": candidates,
        },
    )
    try:
        payload = json.loads(response.text)
    except json.JSONDecodeError:
        payload = {"warnings": ["insufficient canon evidence"]}

    selection = _selection_from_payload(payload)
    if not selection.selected_canon:
        if "insufficient canon evidence" not in selection.warnings:
            selection.warnings.append("insufficient canon evidence")
    return selection

