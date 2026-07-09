"""Minimal LLM client contract for future DeepSeek QA integration.

This module intentionally performs no network calls and reads no API keys at
import time. Concrete providers should be wired by application code or tests.
"""

from dataclasses import dataclass
import json
from typing import Dict, Optional, Protocol


@dataclass
class LLMResponse:
    """Provider-neutral LLM response."""

    text: str
    metadata: Dict


class LLMClient(Protocol):
    """Small interface expected by future narrative QA modules."""

    def complete(
        self,
        prompt: str,
        context: Optional[Dict] = None,
    ) -> LLMResponse:
        """Return one completion for a prompt and optional Context Pack."""


class UnconfiguredLLMClient:
    """Placeholder client used when no real provider has been configured."""

    def complete(
        self,
        prompt: str,
        context: Optional[Dict] = None,
    ) -> LLMResponse:
        """Fail explicitly instead of silently making an ungrounded answer."""
        raise RuntimeError(
            "No LLM provider configured. Configure a DeepSeek-compatible "
            "client in the next Narrative QA layer before calling complete()."
        )


class FakeLLMClient:
    """Deterministic local client for tests and offline CLI demos."""

    def complete(
        self,
        prompt: str,
        context: Optional[Dict] = None,
    ) -> LLMResponse:
        """Return fixed structured outputs for known retrieval tasks."""
        context = context or {}
        task = context.get("task", "")

        if task == "query_rewrite":
            return LLMResponse(
                text=json.dumps(
                    self._rewrite_payload(context.get("question", "")),
                    ensure_ascii=False,
                ),
                metadata={"provider": "fake"},
            )

        if task == "evidence_selection":
            return LLMResponse(
                text=json.dumps(
                    self._selection_payload(
                        context.get("question", ""),
                        context.get("retrieval_plan", {}),
                        context.get("candidates", []),
                    ),
                    ensure_ascii=False,
                ),
                metadata={"provider": "fake"},
            )

        return LLMResponse(text="{}", metadata={"provider": "fake"})

    def _rewrite_payload(self, question: str) -> Dict:
        """Return deterministic retrieval plans for supported questions."""
        if "Rin" in question and ("身份" in question or "是什么" in question):
            return {
                "original_question": question,
                "intent": "character_identity",
                "entities": ["Rin"],
                "rewritten_queries": [
                    "Rin 身份 角色设定",
                    "Rin Nexus-7 android 仿生人",
                    "Rin Tyrell 服务型 娱乐型",
                    "Rin 人物设定",
                ],
                "preferred_source_types": ["character", "worldbuilding"],
                "forbidden_fact_statuses": ["draft", "deprecated", "inspiration"],
                "confidence": "high",
            }

        if "Rain" in question and "Second Foundation" in question:
            return {
                "original_question": question,
                "intent": "relationship",
                "entities": ["Rain", "Second Foundation"],
                "rewritten_queries": [
                    "Rain Second Foundation 关系",
                    "Rain 第二基金会 核心成员",
                    "Rain 组织 关系",
                ],
                "preferred_source_types": ["character", "worldbuilding"],
                "forbidden_fact_statuses": ["draft", "deprecated", "inspiration"],
                "confidence": "high",
            }

        if "Judgment Day" in question:
            return {
                "original_question": question,
                "intent": "concept_definition",
                "entities": ["Judgment Day"],
                "rewritten_queries": [
                    "Judgment Day 事件 定义",
                    "Judgment Day 世界观 时间线",
                ],
                "preferred_source_types": ["worldbuilding", "timeline"],
                "forbidden_fact_statuses": ["draft", "deprecated", "inspiration"],
                "confidence": "high",
            }

        return {
            "original_question": question,
            "intent": "unknown",
            "entities": [],
            "rewritten_queries": [question],
            "preferred_source_types": [],
            "forbidden_fact_statuses": ["draft", "deprecated", "inspiration"],
            "confidence": "low",
        }

    def _selection_payload(
        self,
        question: str,
        retrieval_plan: Dict,
        candidates: list,
    ) -> Dict:
        """Select status-preserving evidence from candidates."""
        selected_canon = []
        selected_draft = []
        selected_deprecated = []
        selected_inspiration = []
        rejected = []
        warnings = []

        for candidate in candidates:
            status = candidate.get("status", "unknown")
            source_file = candidate.get("source_file", "")
            text = candidate.get("text", "")
            reason = self._selection_reason(question, retrieval_plan, candidate)
            enriched = dict(candidate)
            enriched["selection_reason"] = reason

            if status == "canon" and reason:
                selected_canon.append(enriched)
            elif status == "draft":
                selected_draft.append(enriched)
            elif status == "deprecated":
                selected_deprecated.append(enriched)
            elif status == "inspiration":
                selected_inspiration.append(enriched)
            else:
                rejected.append(
                    {
                        "source_file": source_file,
                        "status": status,
                        "reason": "Not selected as grounded evidence.",
                    }
                )

            if len(selected_canon) >= 3:
                break

        if not selected_canon:
            warnings.append("insufficient canon evidence")

        return {
            "selected_canon": selected_canon,
            "selected_draft": selected_draft,
            "selected_deprecated": selected_deprecated,
            "selected_inspiration": selected_inspiration,
            "rejected": rejected,
            "warnings": warnings,
        }

    def _selection_reason(
        self,
        question: str,
        retrieval_plan: Dict,
        candidate: Dict,
    ) -> str:
        """Return a reason when a candidate matches the fake selection policy."""
        source_file = candidate.get("source_file", "")
        text = candidate.get("text", "")
        status = candidate.get("status", "unknown")
        if status != "canon":
            return ""

        if retrieval_plan.get("intent") == "character_identity":
            preferred_sources = (
                "故事大纲与角色设定",
                "STUPID游戏世界观设定集",
                "世界观概述",
            )
            if any(name in source_file for name in preferred_sources):
                return "Canon character/world source selected for Rin identity."
            if "Nexus-7" in text and "Rin" in text:
                return "Canon text mentions Rin and Nexus-7."

        return ""
