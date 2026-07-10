"""Request planner for v1 Daily Narrative Assistant."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from src.llm.client import DeepSeekLLMClient, LLMProviderError, parse_json_object_from_content
from src.v1.chat.response_models import TaskPlan


TASK_TYPES = {"canon_qa", "continuity_check", "story_brief", "art_prompt", "unknown"}


def plan_request(user_request: str, provider: str = "fake", mode: str = "auto") -> TaskPlan:
    if provider == "deepseek":
        try:
            return _plan_with_deepseek(user_request, mode=mode)
        except Exception as exc:  # provider failure must not break assistant UX
            plan = _fake_plan(user_request, provider="fake", mode=mode)
            plan.provider = "fake"
            plan.fallback_reason = f"deepseek_unavailable: {exc}"
            return plan
    return _fake_plan(user_request, provider=provider, mode=mode)


def _plan_with_deepseek(user_request: str, mode: str = "auto") -> TaskPlan:
    client = DeepSeekLLMClient()
    prompt = (
        "Return one JSON object for a game narrative assistant request. "
        "Keys: task_type, user_intent, entities, aliases, branch_scope, "
        "constraints, requested_output, confidence, clarification_needed, "
        "clarification_question, metadata. task_type must be one of: "
        "canon_qa, continuity_check, story_brief, art_prompt, unknown. "
        f"Mode hint: {mode}. User request: {user_request}"
    )
    response = client.complete(prompt, context={"task": "v1_request_planner"})
    payload = parse_json_object_from_content(response.text)
    return _task_plan_from_payload(payload, user_request, provider="deepseek")


def _task_plan_from_payload(payload: Dict[str, Any], user_request: str, provider: str) -> TaskPlan:
    task_type = str(payload.get("task_type", "unknown"))
    if task_type not in TASK_TYPES:
        task_type = "unknown"
    return TaskPlan(
        task_type=task_type,
        user_intent=str(payload.get("user_intent", user_request)),
        entities=list(payload.get("entities", [])),
        aliases=dict(payload.get("aliases", {}) or {}),
        branch_scope=payload.get("branch_scope"),
        constraints=list(payload.get("constraints", [])),
        requested_output=str(payload.get("requested_output", "markdown")),
        confidence=float(payload.get("confidence", 0.0) or 0.0),
        clarification_needed=bool(payload.get("clarification_needed", False)),
        clarification_question=str(payload.get("clarification_question", "")),
        provider=provider,
        metadata=dict(payload.get("metadata", {}) or {}),
    )


def _fake_plan(user_request: str, provider: str = "fake", mode: str = "auto") -> TaskPlan:
    mode_task = _mode_to_task_type(mode)
    task_type = mode_task or _detect_task_type(user_request)
    entities = _extract_entities(user_request)
    branch_scope = _extract_branch_scope(user_request)
    constraints = _extract_constraints(user_request)
    confidence = 0.85 if task_type != "unknown" else 0.25
    return TaskPlan(
        task_type=task_type,
        user_intent=user_request,
        entities=entities,
        aliases=_default_aliases(entities),
        branch_scope=branch_scope,
        constraints=constraints,
        requested_output="markdown",
        confidence=confidence,
        clarification_needed=task_type == "unknown",
        clarification_question=(
            "请说明你想做设定问答、连续性检查、场景 brief，还是美术 prompt。"
            if task_type == "unknown"
            else ""
        ),
        provider=provider,
        metadata={"planner": "fake_keyword_router", "mode": mode},
    )


def _mode_to_task_type(mode: str) -> str | None:
    normalized = str(mode or "auto").strip().lower().replace(" ", "_")
    return {
        "canon_qa": "canon_qa",
        "continuity_check": "continuity_check",
        "story_brief": "story_brief",
        "art_prompt": "art_prompt",
    }.get(normalized)


def _detect_task_type(text: str) -> str:
    lowered = text.lower()
    if any(term in text for term in ("续写", "下一场戏", "场景", "戏")) and not any(
        term in lowered for term in ("prompt", "cg")
    ):
        return "story_brief"
    if any(term in lowered for term in ("prompt", "cg", "art")) or any(
        term in text for term in ("美术", "分镜", "画面")
    ):
        return "art_prompt"
    if any(term in text for term in ("能用吗", "冲突", "覆盖", "当前事实", "这样能用")):
        return "continuity_check"
    if any(term in text for term in ("是什么", "是谁", "身份", "关系", "设定")):
        return "canon_qa"
    return "unknown"


def _extract_entities(text: str) -> List[str]:
    known = ["Rin", "Mouse", "Rain", "Snow", "Larry", "Julie", "Mombasa", "Branch B"]
    entities = [entity for entity in known if entity in text]
    if "鼠" in text and "Mouse" not in entities:
        entities.append("Mouse")
    if "雪" in text and "Snow" not in entities:
        entities.append("Snow")
    if "雨" in text and "Rain" not in entities:
        entities.append("Rain")
    if "第二基地" in text:
        entities.append("Second Foundation")
    return entities


def _default_aliases(entities: List[str]) -> Dict[str, List[str]]:
    aliases = {
        "Mouse": ["鼠"],
        "Rain": ["雨"],
        "Snow": ["雪"],
        "Second Foundation": ["第二基地"],
    }
    return {entity: aliases[entity] for entity in entities if entity in aliases}


def _extract_branch_scope(text: str) -> str | None:
    match = re.search(r"Branch\s*([ABC])|分支\s*([ABC])", text, flags=re.IGNORECASE)
    if not match:
        return None
    branch = match.group(1) or match.group(2)
    return f"Branch {branch.upper()}"


def _extract_constraints(text: str) -> List[str]:
    constraints: List[str] = []
    for phrase in ("克制", "不要暧昧", "不要自动canonize", "不要改Canon"):
        if phrase in text:
            constraints.append(phrase)
    if "右腿" in text:
        constraints.append("mentions right leg")
    if "左腿" in text:
        constraints.append("mentions left leg")
    return constraints
