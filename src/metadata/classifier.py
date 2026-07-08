"""Narrative asset classification placeholder."""

from pathlib import Path
from typing import Dict, Set

from src.metadata.schema import AssetClass, DetectedDomain


STATUS_KEYWORDS = {
    AssetClass.CANON.value: {"canon", "official", "正式", "正史", "已定", "确认", "设定集"},
    AssetClass.DRAFT.value: {"draft", "草稿", "wip", "未定", "备选", "todo"},
    AssetClass.INSPIRATION.value: {"inspiration", "参考", "灵感", "竞品", "ref", "reference"},
    AssetClass.DEPRECATED.value: {"deprecated", "废弃", "旧版", "old", "archive", "弃用"},
    AssetClass.PATTERN.value: {"pattern", "模式", "模板", "结构", "范式"},
}

DOMAIN_KEYWORDS = {
    DetectedDomain.NARRATIVE.value: {
        "plot",
        "story",
        "narrative",
        "scene",
        "dialogue",
        "剧情",
        "故事",
        "叙事",
        "场景",
        "对白",
        "角色",
        "世界观",
    },
    DetectedDomain.SYSTEM.value: {
        "system",
        "mechanic",
        "rule",
        "workflow",
        "系统",
        "机制",
        "规则",
        "数值",
    },
    DetectedDomain.VISUAL.value: {
        "visual",
        "art",
        "image",
        "cg",
        "ui",
        "美术",
        "视觉",
        "立绘",
        "背景",
    },
}


def _score_keywords(haystack: str, candidates: Dict[str, Set[str]]) -> str:
    """Return the first highest-scoring label from a keyword map."""
    scores = {
        label: sum(1 for keyword in keywords if keyword.lower() in haystack)
        for label, keywords in candidates.items()
    }
    best_label = max(scores, key=scores.get)
    return best_label if scores[best_label] > 0 else "unknown"


def classify_asset(text: str, source_metadata: dict) -> dict:
    """Suggest basic status and domain using local path/text keyword rules.

    This function intentionally does not call an LLM. It is a conservative
    first-pass classifier for ingestion metadata drafts.
    """
    source_path = Path(source_metadata.get("source_path", ""))
    path_text = " ".join(part.lower() for part in source_path.parts)
    sample_text = text[:3000].lower()
    haystack = f"{path_text} {sample_text}"

    status = _score_keywords(haystack, STATUS_KEYWORDS)
    detected_domain = _score_keywords(haystack, DOMAIN_KEYWORDS)

    project = "STUPID" if "stupid" in haystack or "审判" in haystack else "unknown"

    return {
        "status": status,
        "detected_domain": detected_domain,
        "project": project,
    }
