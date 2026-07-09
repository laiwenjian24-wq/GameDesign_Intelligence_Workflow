"""Context Pack builder using the experimental LlamaIndex retrieval path."""

from pathlib import Path
from typing import Dict, List

from src.context.context_schema import empty_context_pack
from src.llm.client import FakeLLMClient
from src.rag.llamaindex_ingest import DEFAULT_LLAMA_INDEX_DIR
from src.rag.llamaindex_retriever import retrieve_with_llamaindex
from src.rag.llm_evidence_selector import select_evidence_for_context_pack
from src.rag.llm_query_rewriter import rewrite_query_for_retrieval
from src.retrieval.status_priority import get_usage_rule, group_sources_by_status


def _citation_from_llamaindex_result(result: Dict) -> Dict:
    """Normalize a LlamaIndex retrieval result without losing score or text."""
    return {
        "source_file": result.get("source_file") or result.get("filename", ""),
        "status": result.get("status", "unknown"),
        "summary": result.get("summary", ""),
        "excerpt": result.get("excerpt") or result.get("relevant_excerpt", ""),
        "reason_used": result.get("reason_used", ""),
        "score": result.get("score", 0),
        "retrieval_mode": result.get("retrieval_mode", "unknown"),
        "used_real_llamaindex": result.get("used_real_llamaindex", False),
        "fallback": result.get("fallback", True),
        "text": result.get("text", ""),
        "metadata": result.get("metadata", {}),
    }


def _restriction_for_status(status: str) -> str:
    """Return a human-readable restriction for a source status."""
    return f"{status}: {get_usage_rule(status)}"


def _build_missing_evidence(grouped: Dict[str, List[Dict]]) -> List[str]:
    """Build missing evidence warnings for LlamaIndex Context Packs."""
    missing = []
    if not grouped.get("canon"):
        missing.append("No canon source retrieved. Do not make factual continuity decisions without human review.")
    if grouped.get("unknown"):
        missing.append("Unknown-status sources were retrieved. Treat them as unverified and require human confirmation.")
    return missing


def _build_missing_evidence_from_selection(selection) -> List[str]:
    """Build missing evidence warnings from an LLM evidence selection."""
    missing = []
    missing.extend(selection.missing_evidence)
    for warning in selection.warnings:
        if warning == "insufficient canon evidence":
            missing.append(
                "No canon source selected. Do not make factual continuity decisions without human review."
            )
        else:
            missing.append(warning)
    return missing


def _retrieval_metadata_from_results(retrieval_results: List[Dict]) -> Dict:
    """Build retrieval metadata for CLI/debug output."""
    retrieval_modes = {
        result.get("retrieval_mode", "unknown") for result in retrieval_results
    }
    return {
        "retrieval_mode": "+".join(sorted(retrieval_modes)) if retrieval_modes else "none",
        "used_real_llamaindex": any(
            result.get("used_real_llamaindex", False) for result in retrieval_results
        ),
        "fallback": any(result.get("fallback", True) for result in retrieval_results)
        if retrieval_results
        else True,
    }


def build_context_pack_with_llamaindex(
    task: str,
    top_k: int = 8,
    index_dir: Path = DEFAULT_LLAMA_INDEX_DIR,
    use_llm_assist: bool = False,
    llm_client=None,
) -> Dict:
    """Build a Context Pack using the experimental LlamaIndex retriever."""
    retrieval_plan = None
    evidence_selection = None

    if use_llm_assist:
        llm_client = llm_client or FakeLLMClient()
        retrieval_plan = rewrite_query_for_retrieval(task, llm_client)
        retrieval_results = retrieve_with_llamaindex(
            task,
            top_k=top_k,
            index_dir=index_dir,
            retrieval_plan=retrieval_plan,
            llm_client=llm_client,
            use_llm_rewrite=True,
        )
        evidence_selection = select_evidence_for_context_pack(
            task,
            retrieval_plan,
            retrieval_results,
            llm_client,
        )
    else:
        retrieval_results = retrieve_with_llamaindex(task, top_k=top_k, index_dir=index_dir)

    grouped = group_sources_by_status(retrieval_results)
    context_pack = empty_context_pack(task)

    if evidence_selection is not None:
        context_pack["canon_context"] = [
            _citation_from_llamaindex_result(result)
            for result in evidence_selection.selected_canon
        ]
        context_pack["draft_reference"] = [
            _citation_from_llamaindex_result(result)
            for result in evidence_selection.selected_draft
        ]
        context_pack["deprecated_warnings"] = [
            _citation_from_llamaindex_result(result)
            for result in evidence_selection.selected_deprecated
        ]
        context_pack["inspiration_context"] = [
            _citation_from_llamaindex_result(result)
            for result in evidence_selection.selected_inspiration
        ]
        context_pack["missing_evidence"] = _build_missing_evidence_from_selection(
            evidence_selection
        )
        context_pack["llm_evidence_selection"] = evidence_selection.to_dict()
    else:
        context_pack["canon_context"] = [
            _citation_from_llamaindex_result(result) for result in grouped.get("canon", [])
        ]
        context_pack["draft_reference"] = [
            _citation_from_llamaindex_result(result) for result in grouped.get("draft", [])
        ]
        context_pack["pattern_context"] = [
            _citation_from_llamaindex_result(result) for result in grouped.get("pattern", [])
        ]
        context_pack["inspiration_context"] = [
            _citation_from_llamaindex_result(result)
            for result in grouped.get("inspiration", [])
        ]
        context_pack["deprecated_warnings"] = [
            _citation_from_llamaindex_result(result)
            for result in grouped.get("deprecated", [])
        ]
        context_pack["unverified_context"] = [
            _citation_from_llamaindex_result(result)
            for result in grouped.get("unknown", [])
        ]
        context_pack["missing_evidence"] = _build_missing_evidence(grouped)

    context_pack["restrictions"] = [
        _restriction_for_status("canon"),
        _restriction_for_status("draft"),
        _restriction_for_status("pattern"),
        _restriction_for_status("inspiration"),
        _restriction_for_status("deprecated"),
        _restriction_for_status("unknown"),
    ]
    context_pack["evidence_sources"] = [
        _citation_from_llamaindex_result(result) for result in retrieval_results
    ]
    context_pack["retrieval_metadata"] = _retrieval_metadata_from_results(
        retrieval_results
    )
    if retrieval_plan is not None:
        context_pack["retrieval_plan"] = retrieval_plan.to_dict()

    return context_pack
