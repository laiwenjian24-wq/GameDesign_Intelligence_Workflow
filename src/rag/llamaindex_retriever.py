"""Experimental LlamaIndex retrieval path.

The primary path uses LlamaIndex BM25Retriever. A small lexical fallback remains
only for environments where LlamaIndex dependencies are unavailable.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from src.llm.schemas import RetrievalPlan
from src.rag.llamaindex_ingest import (
    DEFAULT_LLAMA_INDEX_DIR,
    is_real_llamaindex_available,
    load_llamaindex_nodes,
    node_from_serialized,
)
from src.rag.llm_query_rewriter import rewrite_query_for_retrieval
from src.retrieval.status_priority import build_reason_used, get_status_priority


try:
    from llama_index.retrievers.bm25 import BM25Retriever
except ImportError:  # pragma: no cover - exercised in environments without deps.
    BM25Retriever = None


def _tokenize(text: str) -> List[str]:
    """Tokenize English words and CJK character groups conservatively."""
    tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+", text.lower())
    return [token for token in tokens if token.strip()]


def is_real_bm25_available() -> bool:
    """Return whether the LlamaIndex BM25 retriever is available."""
    return is_real_llamaindex_available() and BM25Retriever is not None


def _node_search_text(node: Dict) -> str:
    """Build searchable text from node body and metadata."""
    metadata = node.get("metadata", {})
    return " ".join(
        [
            node.get("text", ""),
            metadata.get("source_file", ""),
            metadata.get("status", ""),
            metadata.get("asset_type", ""),
            " ".join(metadata.get("tags", [])),
            metadata.get("reason", ""),
            metadata.get("expected_usage", ""),
        ]
    )


def _fallback_score(query_tokens: List[str], node: Dict) -> float:
    """Score nodes without rank-bm25 installed."""
    searchable = _node_search_text(node).lower()
    return float(sum(searchable.count(token) for token in query_tokens))


def _excerpt(text: str, query_tokens: List[str], max_length: int = 260) -> str:
    """Build a short excerpt around the first query term."""
    if not text:
        return ""

    lower_text = text.lower()
    positions = [lower_text.find(token) for token in query_tokens]
    positions = [position for position in positions if position >= 0]
    start = max(min(positions) - 60, 0) if positions else 0
    excerpt = re.sub(r"\s+", " ", text[start : start + max_length]).strip()
    if start > 0:
        excerpt = f"...{excerpt}"
    if start + max_length < len(text):
        excerpt = f"{excerpt}..."
    return excerpt


def _result_from_node(
    node: Dict,
    score: float,
    query_tokens: List[str],
    retrieval_mode: str,
    used_real_llamaindex: bool,
    matched_query: str = "",
) -> Dict:
    """Normalize one node hit to the Context Pack compatible shape."""
    metadata = node.get("metadata", {})
    status = metadata.get("status", "unknown")
    source_file = metadata.get("source_file", "")
    text = node.get("text", "")
    usage_rule = build_reason_used(status, int(score)).split("rule=", 1)[-1]

    return {
        "text": text,
        "source_file": source_file,
        "filename": source_file,
        "status": status,
        "score": score,
        "raw_score": score,
        "matched_query": matched_query,
        "matched_query_count": 1 if matched_query else 0,
        "retrieval_mode": retrieval_mode,
        "retrieval_mode_detail": retrieval_mode,
        "used_real_llamaindex": used_real_llamaindex,
        "fallback": not used_real_llamaindex,
        "metadata": metadata,
        "summary": metadata.get("reason", ""),
        "excerpt": _excerpt(text, query_tokens),
        "relevant_excerpt": _excerpt(text, query_tokens),
        "file_path": metadata.get("file_path", ""),
        "reason_used": (
            f"retrieval_mode={retrieval_mode}; score={score:.4f}; "
            f"status={status}; status_priority={get_status_priority(status)}; "
            f"rule={usage_rule}"
        ),
    }


def _serialized_from_node_with_score(node_with_score) -> Dict:
    """Convert a LlamaIndex NodeWithScore to the local result node shape."""
    node = node_with_score.node
    if hasattr(node, "get_content"):
        text = node.get_content()
    else:
        text = getattr(node, "text", "")
    return {
        "text": text,
        "metadata": getattr(node, "metadata", {}) or {},
        "score": float(node_with_score.score or 0),
    }


def _retrieve_with_real_bm25(
    nodes: List[Dict],
    query: str,
    top_k: int,
    retrieval_mode: str = "bm25",
) -> List[Dict]:
    """Retrieve with LlamaIndex BM25Retriever."""
    llama_nodes = [node_from_serialized(node) for node in nodes]
    retriever = BM25Retriever.from_defaults(
        nodes=llama_nodes,
        similarity_top_k=top_k,
    )
    hits = retriever.retrieve(query)
    query_tokens = _tokenize(query)

    return [
        _result_from_node(
            {
                "text": item["text"],
                "metadata": item["metadata"],
            },
            item["score"],
            query_tokens,
            retrieval_mode=retrieval_mode,
            used_real_llamaindex=True,
            matched_query=query,
        )
        for item in (_serialized_from_node_with_score(hit) for hit in hits)
    ]


def _retrieve_with_fallback(
    nodes: List[Dict],
    query: str,
    top_k: int,
    retrieval_mode: str = "fallback",
) -> List[Dict]:
    """Fallback lexical retrieval used only when LlamaIndex is unavailable."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    results = []
    for node in nodes:
        score = _fallback_score(query_tokens, node)
        if score <= 0:
            continue
        results.append(
            _result_from_node(
                node,
                score,
                query_tokens,
                retrieval_mode=retrieval_mode,
                used_real_llamaindex=False,
                matched_query=query,
            )
        )

    results.sort(
        key=lambda item: (
            -item["score"],
            -get_status_priority(item.get("status", "unknown")),
            item.get("source_file", ""),
        )
    )
    return results[:top_k]


def _retrieve_single_query(
    nodes: List[Dict],
    query: str,
    top_k: int,
    retrieval_mode: str,
) -> List[Dict]:
    """Retrieve one query through the real LlamaIndex path or fallback."""
    if is_real_bm25_available():
        return _retrieve_with_real_bm25(nodes, query, top_k, retrieval_mode)
    return _retrieve_with_fallback(nodes, query, top_k, "fallback")


def _merge_multi_query_results(results_by_query: List[List[Dict]]) -> List[Dict]:
    """Merge multi-query candidates without performing complex ranking."""
    merged: Dict[tuple, Dict] = {}
    for results in results_by_query:
        for result in results:
            key = (result.get("source_file", ""), result.get("text", "")[:240])
            matched_query = result.get("matched_query", "")
            if key not in merged:
                item = dict(result)
                item["matched_queries"] = [matched_query] if matched_query else []
                item["matched_query_count"] = len(item["matched_queries"])
                merged[key] = item
                continue

            item = merged[key]
            if matched_query and matched_query not in item["matched_queries"]:
                item["matched_queries"].append(matched_query)
            item["matched_query_count"] = len(item["matched_queries"])
            if result.get("raw_score", 0) > item.get("raw_score", 0):
                item["raw_score"] = result.get("raw_score", 0)
                item["score"] = result.get("score", 0)
                item["matched_query"] = matched_query

    return list(merged.values())


def retrieve_with_llamaindex(
    query: str,
    top_k: int = 8,
    index_dir: Path = DEFAULT_LLAMA_INDEX_DIR,
    retrieval_plan: Optional[RetrievalPlan] = None,
    llm_client=None,
    use_llm_rewrite: bool = False,
) -> List[Dict]:
    """Retrieve from the experimental LlamaIndex node store."""
    nodes = load_llamaindex_nodes(index_dir)
    if not nodes or not query.strip():
        return []

    if use_llm_rewrite:
        if retrieval_plan is None:
            if llm_client is None:
                raise ValueError("llm_client is required when use_llm_rewrite=True")
            retrieval_plan = rewrite_query_for_retrieval(query, llm_client)
        rewritten_queries = retrieval_plan.rewritten_queries or [query]
        results_by_query = [
            _retrieve_single_query(
                nodes,
                rewritten_query,
                top_k,
                "bm25_llm_rewrite",
            )
            for rewritten_query in rewritten_queries
        ]
        merged = _merge_multi_query_results(results_by_query)
        for item in merged:
            item["retrieval_plan"] = retrieval_plan.to_dict()
        return merged[: max(top_k, len(merged))]

    return _retrieve_single_query(nodes, query, top_k, "bm25")
