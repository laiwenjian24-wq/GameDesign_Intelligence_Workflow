"""Hybrid retrieval helpers for the experimental v0.4 path."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.rag.llamaindex_ingest import DEFAULT_LLAMA_INDEX_DIR
from src.rag.llamaindex_retriever import retrieve_with_llamaindex
from src.retrieval.query import query_knowledge_base


def _key(result: Dict) -> Tuple[str, str]:
    """Return a stable key for reciprocal rank fusion."""
    return (result.get("source_file", ""), result.get("excerpt", "")[:80])


def retrieve_with_hybrid(
    query: str,
    top_k: int = 8,
    llamaindex_dir: Path = DEFAULT_LLAMA_INDEX_DIR,
    keyword_index_dir: Optional[Path] = None,
) -> List[Dict]:
    """Fuse LlamaIndex node retrieval with the existing keyword fallback."""
    ranked_lists = [retrieve_with_llamaindex(query, top_k=top_k, index_dir=llamaindex_dir)]
    if keyword_index_dir is not None:
        ranked_lists.append(query_knowledge_base(query, keyword_index_dir, top_k=top_k))

    fused: Dict[Tuple[str, str], Dict] = {}
    for ranked in ranked_lists:
        for rank, result in enumerate(ranked, start=1):
            key = _key(result)
            if key not in fused:
                fused[key] = dict(result)
                fused[key]["fusion_score"] = 0.0
            fused[key]["fusion_score"] += 1.0 / (60 + rank)

    results = list(fused.values())
    results.sort(key=lambda item: (-item.get("fusion_score", 0.0), item.get("source_file", "")))
    return results[:top_k]

