"""Canon QA task for the Daily Narrative Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import (
    CANON_POLICY,
    DEPRECATED_POLICY,
    DRAFT_POLICY,
    INSPIRATION_POLICY,
    NO_AUTO_CANON_POLICY,
)


def run_canon_qa(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    if "Rin" in user_request and ("身份" in user_request or "是什么" in user_request):
        answer = (
            "MVP demo answer: Rin 应作为需要 Canon 证据支持的角色身份问题处理。"
            "在当前 fake provider 下，助手不会声称已完成最终考据；它会提示从 Canon "
            "Context Pack 读取角色身份证据后再输出正式答案。"
        )
        next_step = "用 v0.4 `ask-rag` 或后续 v1 JSON Context Pack 检索 Rin 的 Canon 身份证据。"
    else:
        answer = "Missing Evidence / Needs Review: fake provider 没有足够规则回答该设定问题。"
        next_step = "补充 Canon evidence，或使用 opt-in DeepSeek provider 做人工审阅辅助。"
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="canon_qa",
        answer_markdown=answer,
        evidence_or_source_policy=[
            CANON_POLICY,
            DRAFT_POLICY,
            DEPRECATED_POLICY,
            INSPIRATION_POLICY,
            NO_AUTO_CANON_POLICY,
        ],
        risks_or_limitations=[
            "Fake provider returns a deterministic demo response, not final canon research.",
            "Draft, Deprecated, and Inspiration material cannot answer as current fact.",
        ],
        suggested_next_step=next_step,
        debug_task_plan=plan.to_dict(),
        provider=plan.provider,
    )
