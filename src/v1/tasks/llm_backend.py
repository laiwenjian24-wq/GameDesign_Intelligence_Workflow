"""Opt-in real LLM helpers for v1 terminal capability tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.context.llamaindex_context_builder import build_context_pack_with_llamaindex
from src.llm.client import DeepSeekLLMClient, LLMProviderError, parse_json_object_from_content
from src.rag.llamaindex_ingest import build_llamaindex_nodes


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LLAMA_INDEX_DIR = PROJECT_ROOT / "knowledge_base" / "llama_index"


def build_retrieval_context(query: str) -> Tuple[Dict[str, Any], List[str]]:
    """Build a non-LLM-assisted Context Pack using the existing v0.4 RAG path."""
    warnings: List[str] = []
    try:
        build_llamaindex_nodes(index_dir=LLAMA_INDEX_DIR)
        context_pack = build_context_pack_with_llamaindex(
            query,
            top_k=8,
            index_dir=LLAMA_INDEX_DIR,
            use_llm_assist=False,
        )
    except Exception as exc:
        warnings.append(f"retrieval_failed: {exc}")
        context_pack = {
            "canon_context": [],
            "draft_reference": [],
            "deprecated_warnings": [],
            "inspiration_context": [],
            "missing_evidence": ["Retrieval failed; no Canon evidence available."],
        }
    return context_pack, warnings


def has_canon_evidence(context_pack: Dict[str, Any]) -> bool:
    return bool(context_pack.get("canon_context"))


def context_pack_from_lite_evidence(evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped = {
        "canon_context": [],
        "draft_reference": [],
        "deprecated_warnings": [],
        "inspiration_context": [],
        "missing_evidence": [],
    }
    for item in evidence:
        status = item.get("status", "unknown")
        if status == "canon":
            grouped["canon_context"].append(item)
        elif status == "draft":
            grouped["draft_reference"].append(item)
        elif status == "deprecated":
            grouped["deprecated_warnings"].append(item)
        elif status == "inspiration":
            grouped["inspiration_context"].append(item)
    if not grouped["canon_context"]:
        grouped["missing_evidence"].append("No canon evidence retrieved from Lite KB.")
    return grouped


def evidence_snippet_markdown(evidence: List[Dict[str, Any]], limit: int = 5) -> str:
    if not evidence:
        return "- No Lite KB evidence retrieved."
    lines = []
    for item in evidence[:limit]:
        lines.append(
            f"- `{item.get('source_file', '')}` [{item.get('status', 'unknown')}] "
            f"{item.get('section_title', '')}: {item.get('excerpt', '')}"
        )
    return "\n".join(lines)


def source_policy_lines() -> List[str]:
    return [
        "Canon is current truth.",
        "Draft is reference only and cannot override Canon.",
        "Deprecated is historical/conflict evidence only and cannot be used as current truth.",
        "Inspiration is not fact.",
        "LLM cannot automatically canonize new material.",
    ]


def call_deepseek_markdown(
    task_name: str,
    user_request: str,
    context_pack: Dict[str, Any],
    output_contract: str,
) -> Dict[str, Any]:
    """Call DeepSeek and require a compact JSON object with Markdown content."""
    prompt = (
        "You are a Canon-aware narrative game design assistant. "
        "Return valid JSON only. Do not wrap in markdown. "
        "Use the supplied Context Pack as evidence. Canon is current truth. "
        "Draft is reference only. Deprecated is historical/conflict evidence only. "
        "Inspiration is not fact. Do not automatically canonize new material. "
        "If Canon evidence is missing, return NEEDS_REVIEW or Missing Evidence. "
        "Return keys: answer_markdown, risks_or_limitations, suggested_next_step. "
        f"Task: {task_name}. Output contract: {output_contract}. "
        f"User request: {user_request}\n"
        f"Context Pack: {json.dumps(context_pack, ensure_ascii=False)}"
    )
    client = DeepSeekLLMClient()
    response = client.complete(prompt, context={"task": "v1_daily_assistant"})
    payload = parse_json_object_from_content(response.text)
    return {
        "answer_markdown": str(payload.get("answer_markdown", "")).strip(),
        "risks_or_limitations": list(payload.get("risks_or_limitations", [])),
        "suggested_next_step": str(payload.get("suggested_next_step", "")).strip(),
        "raw_payload": payload,
    }


def missing_evidence_payload(reason: str) -> Dict[str, Any]:
    return {
        "answer_markdown": f"### Decision: NEEDS_REVIEW\n\nMissing Evidence: {reason}",
        "risks_or_limitations": [
            "No reliable Canon evidence was available.",
            "Draft, Deprecated, and Inspiration cannot be used as current fact.",
        ],
        "suggested_next_step": "Retrieve or add reviewed Canon evidence before making a production decision.",
        "raw_payload": {},
    }
