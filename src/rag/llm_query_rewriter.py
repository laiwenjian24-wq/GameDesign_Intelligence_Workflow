"""LLM-assisted query rewriting for LlamaIndex retrieval."""

import json
from typing import Dict

from src.llm.schemas import RetrievalPlan


def _plan_from_payload(question: str, payload: Dict) -> RetrievalPlan:
    """Build a RetrievalPlan with conservative defaults."""
    rewritten_queries = payload.get("rewritten_queries") or [question]
    return RetrievalPlan(
        original_question=payload.get("original_question", question),
        intent=payload.get("intent", "unknown"),
        entities=list(payload.get("entities", [])),
        rewritten_queries=list(rewritten_queries),
        preferred_source_types=list(payload.get("preferred_source_types", [])),
        forbidden_fact_statuses=list(
            payload.get(
                "forbidden_fact_statuses",
                ["draft", "deprecated", "inspiration"],
            )
        ),
        confidence=payload.get("confidence", "low"),
    )


def rewrite_query_for_retrieval(question: str, llm_client) -> RetrievalPlan:
    """Ask an LLM client for retrieval-only query understanding."""
    response = llm_client.complete(
        "Rewrite the narrative question into retrieval queries only.",
        context={"task": "query_rewrite", "question": question},
    )
    try:
        payload = json.loads(response.text)
    except json.JSONDecodeError:
        payload = {}
    return _plan_from_payload(question, payload)

