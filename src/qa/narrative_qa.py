"""Evidence-grounded narrative QA over Full-context and RAG context inputs."""

import json
from typing import Dict, List

from src.llm.client import LLMClient, parse_json_object_from_content
from src.llm.schemas import QAAnswer


QA_JSON_KEYS = [
    "answer",
    "confidence",
    "canon_sources",
    "draft_notes",
    "deprecated_warnings",
    "missing_evidence",
    "limitations",
]


def _source_label(item: Dict) -> str:
    """Return a compact source label for QA reports."""
    source_file = item.get("source_file", "")
    metadata = item.get("metadata", {}) or {}
    section_title = metadata.get("section_title") or metadata.get("heading")
    if section_title:
        return f"{source_file}#{section_title}"
    return source_file


def _compact_document(document: Dict, text_limit: int = 1800) -> Dict:
    """Keep only fields needed by the answer prompt."""
    text = document.get("text", "")
    return {
        "source_file": document.get("source_file", ""),
        "status": document.get("status", ""),
        "asset_type": document.get("asset_type", ""),
        "text": text[:text_limit],
    }


def _compact_evidence(evidence: Dict, text_limit: int = 1800) -> Dict:
    """Keep only fields needed by the answer prompt."""
    text = evidence.get("text") or evidence.get("excerpt", "")
    metadata = evidence.get("metadata", {}) or {}
    return {
        "source_file": evidence.get("source_file", ""),
        "status": evidence.get("status", ""),
        "section_title": metadata.get("section_title") or metadata.get("heading", ""),
        "excerpt": evidence.get("excerpt", ""),
        "text": text[:text_limit],
    }


def _qa_answer_from_payload(payload: Dict) -> QAAnswer:
    """Convert a provider JSON payload into a QAAnswer."""
    return QAAnswer(
        answer=str(payload.get("answer", "")),
        confidence=str(payload.get("confidence", "low")),
        canon_sources=list(payload.get("canon_sources", [])),
        draft_notes=list(payload.get("draft_notes", [])),
        deprecated_warnings=list(payload.get("deprecated_warnings", [])),
        missing_evidence=list(payload.get("missing_evidence", [])),
        limitations=list(payload.get("limitations", [])),
    )


def _fallback_no_canon_answer(question: str, mode: str, missing: List[str]) -> Dict:
    """Return a deterministic insufficient-evidence report."""
    answer = QAAnswer(
        answer="Insufficient canon evidence to answer this question.",
        confidence="low",
        canon_sources=[],
        draft_notes=[],
        deprecated_warnings=[],
        missing_evidence=missing or ["No canon evidence available."],
        limitations=[
            "Draft, deprecated, and inspiration material cannot be used as current fact."
        ],
    )
    return {
        "question": question,
        "mode": mode,
        "answer": answer.to_dict(),
    }


def _build_full_context_prompt(question: str, compact_context: Dict) -> str:
    """Build the Full-context answer prompt."""
    schema = {key: [] for key in QA_JSON_KEYS}
    schema["answer"] = "short grounded answer"
    schema["confidence"] = "high|medium|low"
    return (
        "You are answering a game narrative question from a governed "
        "Full-context Bundle. Return valid JSON only. Do not wrap in markdown. "
        "Canon documents are the only source of current truth. Draft documents "
        "are reference only and must not override Canon. Deprecated documents "
        "are historical/conflict evidence only and are not current truth. "
        "Inspiration documents are not fact. If Canon has no evidence, say "
        "insufficient evidence. Cite source_file names.\n\n"
        f"JSON schema example: {json.dumps(schema, ensure_ascii=False)}\n\n"
        f"Question: {question}\n\n"
        f"Context: {json.dumps(compact_context, ensure_ascii=False)}"
    )


def _build_rag_prompt(question: str, compact_context: Dict) -> str:
    """Build the RAG Context Pack answer prompt."""
    schema = {key: [] for key in QA_JSON_KEYS}
    schema["answer"] = "short grounded answer"
    schema["confidence"] = "high|medium|low"
    return (
        "You are answering a game narrative question from a Context Pack. "
        "Return valid JSON only. Do not wrap in markdown. Only answer from "
        "canon_context. draft_reference is reference only. deprecated_warnings "
        "are not current truth. inspiration_context is not fact. If canon_context "
        "is empty, say insufficient evidence. Cite source_file names and "
        "section_title when available.\n\n"
        f"JSON schema example: {json.dumps(schema, ensure_ascii=False)}\n\n"
        f"Question: {question}\n\n"
        f"Context Pack: {json.dumps(compact_context, ensure_ascii=False)}"
    )


def answer_from_full_context(
    question: str,
    full_context_bundle: Dict,
    llm_client: LLMClient,
    provider: str = "fake",
) -> Dict:
    """Generate a grounded QA report from a Full-context Bundle."""
    canon_documents = full_context_bundle.get("groups", {}).get("canon", [])
    if not canon_documents:
        return _fallback_no_canon_answer(
            question,
            "full-context",
            ["No canon documents are available in the Full-context Bundle."],
        )

    compact_context = {
        "canon": [_compact_document(item) for item in canon_documents],
        "draft": [
            _compact_document(item)
            for item in full_context_bundle.get("groups", {}).get("draft", [])
        ],
        "deprecated": [
            _compact_document(item)
            for item in full_context_bundle.get("groups", {}).get("deprecated", [])
        ],
        "inspiration": [
            _compact_document(item)
            for item in full_context_bundle.get("groups", {}).get("inspiration", [])
        ],
    }
    prompt = _build_full_context_prompt(question, compact_context)
    response = llm_client.complete(
        prompt,
        context={
            "task": "narrative_qa",
            "mode": "full-context",
            "question": question,
            "context": compact_context,
        },
    )
    payload = parse_json_object_from_content(response.text)
    return {
        "question": question,
        "mode": "full-context",
        "provider": provider,
        "answer": _qa_answer_from_payload(payload).to_dict(),
    }


def answer_from_rag_context_pack(
    question: str,
    context_pack: Dict,
    llm_client: LLMClient,
    provider: str = "fake",
) -> Dict:
    """Generate a grounded QA report from a RAG Context Pack."""
    canon_context = context_pack.get("canon_context", [])
    if not canon_context:
        return _fallback_no_canon_answer(
            question,
            "rag-context-pack",
            context_pack.get("missing_evidence", [])
            or ["No canon_context evidence is available."],
        )

    compact_context = {
        "canon_context": [_compact_evidence(item) for item in canon_context],
        "draft_reference": [
            _compact_evidence(item) for item in context_pack.get("draft_reference", [])
        ],
        "deprecated_warnings": [
            _compact_evidence(item)
            for item in context_pack.get("deprecated_warnings", [])
        ],
        "inspiration_context": [
            _compact_evidence(item)
            for item in context_pack.get("inspiration_context", [])
        ],
        "missing_evidence": context_pack.get("missing_evidence", []),
    }
    prompt = _build_rag_prompt(question, compact_context)
    response = llm_client.complete(
        prompt,
        context={
            "task": "narrative_qa",
            "mode": "rag-context-pack",
            "question": question,
            "context": compact_context,
        },
    )
    payload = parse_json_object_from_content(response.text)
    answer = _qa_answer_from_payload(payload)
    if not answer.canon_sources:
        answer.missing_evidence.append("No canon sources cited by answer provider.")
        answer.confidence = "low"
    return {
        "question": question,
        "mode": "rag-context-pack",
        "provider": provider,
        "answer": answer.to_dict(),
    }
