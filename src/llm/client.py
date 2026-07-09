"""Minimal LLM client contract for future DeepSeek QA integration.

This module intentionally performs no network calls and reads no API keys at
import time. Concrete providers should be wired by application code or tests.
"""

from dataclasses import dataclass
import json
import os
import re
from typing import Any
from typing import Dict, Optional, Protocol
from urllib import error, request


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


class LLMProviderError(RuntimeError):
    """Clear provider error suitable for CLI display."""


def _sanitize_response_preview(content: str, limit: int = 300) -> str:
    """Return a short response preview safe for error messages."""
    compact = re.sub(r"\s+", " ", content or "").strip()
    return compact[:limit]


def parse_json_object_from_content(content: str) -> Dict:
    """Parse a JSON object from raw or fenced LLM content."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        return payload

    fence_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        content or "",
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fence_match:
        try:
            payload = json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            return payload

    preview = _sanitize_response_preview(content)
    raise LLMProviderError(
        "DeepSeek response was not valid JSON. "
        f"Sanitized response preview: {preview}"
    )


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


class DeepSeekLLMClient:
    """DeepSeek chat client for retrieval planning and evidence selection only."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        if not self.api_key:
            raise LLMProviderError(
                "DEEPSEEK_API_KEY is not set. Set it in the environment before "
                "using --provider deepseek."
            )
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(
        self,
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        require_json: bool = True,
    ) -> str:
        """Call DeepSeek chat completion and return assistant content."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if require_json:
            payload["response_format"] = {"type": "json_object"}

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMProviderError(f"DeepSeek API HTTP error: {exc.code}; {detail}") from exc
        except (error.URLError, TimeoutError) as exc:
            raise LLMProviderError(f"DeepSeek API request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMProviderError("DeepSeek API returned invalid JSON.") from exc

        try:
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "DeepSeek API response did not contain choices[0].message.content."
            ) from exc

        if require_json:
            parse_json_object_from_content(content)
        return content

    def complete(
        self,
        prompt: str,
        context: Optional[Dict] = None,
    ) -> LLMResponse:
        """Return structured JSON for query rewrite or evidence selection."""
        context = context or {}
        task = context.get("task", "")
        if task == "query_rewrite":
            messages = self._query_rewrite_messages(context.get("question", ""))
        elif task == "evidence_selection":
            messages = self._evidence_selection_messages(context)
        elif task == "narrative_qa":
            messages = self._narrative_qa_messages(context)
        else:
            messages = [
                {
                    "role": "system",
                    "content": "Return a JSON object only.",
                },
                {"role": "user", "content": prompt},
            ]

        content = self.chat(messages, temperature=0.0, max_tokens=4096, require_json=True)
        return LLMResponse(text=content, metadata={"provider": "deepseek"})

    def _query_rewrite_messages(self, question: str) -> list:
        """Build messages for retrieval-only query planning."""
        return [
            {
                "role": "system",
                "content": (
                    "You are a retrieval planner for a game narrative knowledge base. "
                    "Do not answer the user question. Return valid JSON only. "
                    "Do not wrap in markdown. Do not include explanations. "
                    "Return one JSON object with keys: "
                    "original_question, intent, entities, rewritten_queries, "
                    "preferred_source_types, forbidden_fact_statuses, confidence. "
                    "Use concise Chinese and English search phrases where useful. "
                    "forbidden_fact_statuses must include draft, deprecated, inspiration "
                    "for fact questions. Example: "
                    '{"original_question":"Rin是什么身份？","intent":"character_identity",'
                    '"entities":["Rin"],"rewritten_queries":["Rin 身份 角色设定",'
                    '"Rin Nexus-7 仿生人"],"preferred_source_types":["character",'
                    '"worldbuilding"],"forbidden_fact_statuses":["draft","deprecated",'
                    '"inspiration"],"confidence":"high"}'
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return valid JSON only for this question. Do not wrap in markdown. "
                    f"Question: {question}"
                ),
            },
        ]

    def _evidence_selection_messages(self, context: Dict) -> list:
        """Build messages for status-preserving evidence selection."""
        payload = {
            "question": context.get("question", ""),
            "retrieval_plan": context.get("retrieval_plan", {}),
            "candidates": context.get("candidates", []),
        }
        return [
            {
                "role": "system",
                "content": (
                    "You select evidence for a Context Pack. Do not answer the "
                    "question. Return valid JSON only. Do not wrap in markdown. "
                    "Do not include explanations. Return candidate_id values only. "
                    "Do not return full text, markdown excerpts, or explanations. "
                    "Preserve every candidate status exactly. Never put draft, "
                    "deprecated, or inspiration evidence into selected_canon_ids. "
                    "If no canon candidate supports the fact, include warning "
                    "'insufficient canon evidence'. Return one JSON object with keys: "
                    "selected_canon_ids, selected_draft_ids, selected_deprecated_ids, "
                    "selected_inspiration_ids, rejected_ids, warnings, missing_evidence. "
                    "Example: "
                    '{"selected_canon_ids":["c001"],"selected_draft_ids":[],'
                    '"selected_deprecated_ids":[],"selected_inspiration_ids":[],'
                    '"rejected_ids":["c002"],"warnings":[],"missing_evidence":[]}'
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return valid JSON only for this evidence selection task. "
                    "Do not wrap in markdown.\n"
                    + json.dumps(payload, ensure_ascii=False)
                ),
            },
        ]

    def _narrative_qa_messages(self, context: Dict) -> list:
        """Build messages for evidence-grounded narrative QA."""
        payload = {
            "mode": context.get("mode", ""),
            "question": context.get("question", ""),
            "context": context.get("context", {}),
        }
        return [
            {
                "role": "system",
                "content": (
                    "You answer questions for a governed game narrative knowledge "
                    "base. Return valid JSON only. Do not wrap in markdown. Do not "
                    "include explanations outside JSON. Canon is the only source of "
                    "current truth. Draft is reference only. Deprecated is historical "
                    "or conflict evidence only and is not current truth. Inspiration "
                    "is not fact. If canon evidence is missing, answer insufficient "
                    "evidence. Cite source_file names and section_title when present. "
                    "Return one JSON object with keys: answer, confidence, "
                    "canon_sources, draft_notes, deprecated_warnings, "
                    "missing_evidence, limitations. Example: "
                    '{"answer":"Rin is a Nexus-7 android.","confidence":"high",'
                    '"canon_sources":["story.md#Rin"],"draft_notes":[],'
                    '"deprecated_warnings":[],"missing_evidence":[],"limitations":[]}'
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return valid JSON only for this narrative QA task. "
                    "Do not wrap in markdown.\n"
                    + json.dumps(payload, ensure_ascii=False)
                ),
            },
        ]


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

        if task == "narrative_qa":
            return LLMResponse(
                text=json.dumps(
                    self._qa_payload(
                        context.get("question", ""),
                        context.get("mode", ""),
                        context.get("context", {}),
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
        selected_canon_ids = []
        selected_draft_ids = []
        selected_deprecated_ids = []
        selected_inspiration_ids = []
        rejected_ids = []
        warnings = []
        missing_evidence = []

        for candidate in candidates:
            status = candidate.get("status", "unknown")
            candidate_id = candidate.get("candidate_id", "")
            reason = self._selection_reason(question, retrieval_plan, candidate)

            if status == "canon" and reason:
                selected_canon_ids.append(candidate_id)
            elif status == "draft":
                selected_draft_ids.append(candidate_id)
            elif status == "deprecated":
                selected_deprecated_ids.append(candidate_id)
            elif status == "inspiration":
                selected_inspiration_ids.append(candidate_id)
            else:
                rejected_ids.append(candidate_id)

            if len(selected_canon_ids) >= 3:
                break

        if not selected_canon_ids:
            warnings.append("insufficient canon evidence")
            missing_evidence.append("no canon evidence selected")

        return {
            "selected_canon_ids": selected_canon_ids,
            "selected_draft_ids": selected_draft_ids,
            "selected_deprecated_ids": selected_deprecated_ids,
            "selected_inspiration_ids": selected_inspiration_ids,
            "rejected_ids": rejected_ids,
            "warnings": warnings,
            "missing_evidence": missing_evidence,
        }

    def _selection_reason(
        self,
        question: str,
        retrieval_plan: Dict,
        candidate: Dict,
    ) -> str:
        """Return a reason when a candidate matches the fake selection policy."""
        source_file = candidate.get("source_file", "")
        excerpt = candidate.get("excerpt", "")
        status = candidate.get("status", "unknown")
        if status != "canon":
            return ""

        if retrieval_plan.get("intent") == "character_identity":
            heading = candidate.get("heading", "") or candidate.get("section_title", "")
            if "Rin" in heading and (
                "Nexus-7" in heading or "仿生人" in heading or "身份" in heading
            ):
                return "Canon character identity section selected for Rin."
            if "Nexus-7" in excerpt and "Rin" in excerpt:
                return "Canon text mentions Rin and Nexus-7."

        return ""

    def _qa_payload(self, question: str, mode: str, qa_context: Dict) -> Dict:
        """Return a deterministic grounded QA answer for offline tests."""
        canon_items = qa_context.get("canon_context") or qa_context.get("canon") or []
        draft_items = qa_context.get("draft_reference") or qa_context.get("draft") or []
        deprecated_items = (
            qa_context.get("deprecated_warnings") or qa_context.get("deprecated") or []
        )

        if not canon_items:
            return {
                "answer": "Insufficient canon evidence to answer this question.",
                "confidence": "low",
                "canon_sources": [],
                "draft_notes": [],
                "deprecated_warnings": [
                    item.get("source_file", "") for item in deprecated_items
                ],
                "missing_evidence": ["No canon evidence available."],
                "limitations": [
                    "Draft, deprecated, and inspiration material cannot be used as current fact."
                ],
            }

        canon_text = "\n".join(
            str(item.get("text", "")) + "\n" + str(item.get("excerpt", ""))
            for item in canon_items
        )
        canon_sources = [
            self._qa_source_label(item)
            for item in canon_items
            if item.get("source_file", "")
        ]
        deprecated_sources = [
            item.get("source_file", "") for item in deprecated_items if item.get("source_file")
        ]
        draft_sources = [
            item.get("source_file", "") for item in draft_items if item.get("source_file")
        ]

        if "Rin" in question and ("Nexus-7" in canon_text or "android" in canon_text):
            return {
                "answer": "Rin is identified by canon evidence as a Nexus-7 android.",
                "confidence": "high",
                "canon_sources": canon_sources[:3],
                "draft_notes": draft_sources[:3],
                "deprecated_warnings": deprecated_sources[:3],
                "missing_evidence": [],
                "limitations": [
                    "Answer is limited to the provided canon evidence."
                ],
            }

        return {
            "answer": "Canon evidence is present, but the fake provider cannot infer a reliable answer for this question.",
            "confidence": "low",
            "canon_sources": canon_sources[:3],
            "draft_notes": draft_sources[:3],
            "deprecated_warnings": deprecated_sources[:3],
            "missing_evidence": ["Fake provider has no deterministic answer rule."],
            "limitations": ["Use --provider deepseek for a manual broader-language test."],
        }

    def _qa_source_label(self, item: Dict) -> str:
        """Return source label with section title when available."""
        source_file = item.get("source_file", "")
        section_title = item.get("section_title", "")
        if not section_title:
            metadata = item.get("metadata", {}) or {}
            section_title = metadata.get("section_title") or metadata.get("heading", "")
        if section_title:
            return f"{source_file}#{section_title}"
        return source_file
