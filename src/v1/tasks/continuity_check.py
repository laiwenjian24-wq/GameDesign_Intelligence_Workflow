"""Minimal governance continuity check task for the Daily Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import (
    CANON_POLICY,
    DEPRECATED_POLICY,
    DRAFT_POLICY,
    INSPIRATION_POLICY,
    NO_AUTO_CANON_POLICY,
)


def run_continuity_check_task(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    decision = "NEEDS_REVIEW"
    issues = []
    suggested_fix = "Retrieve branch-specific Canon evidence before accepting this content."

    if any(term in user_request for term in ("Deprecated", "废弃", "旧版", "覆盖当前Canon")):
        decision = "FAIL"
        issues.append("Deprecated material cannot be used as current truth or override Canon.")
        suggested_fix = "Keep deprecated material as conflict history only."
    if any(term in user_request for term in ("草稿", "Draft")) and "覆盖" in user_request:
        decision = "FAIL"
        issues.append("Draft material cannot override Canon.")
        suggested_fix = "Use human canonization review before promoting draft material."
    if "灵感" in user_request and ("事实" in user_request or "当前" in user_request):
        decision = "FAIL"
        issues.append("Inspiration cannot be used as factual evidence.")
        suggested_fix = "Use inspiration as thematic reference only."
    if not issues:
        issues.append("Canon evidence is required; this MVP does not perform full semantic verification.")

    answer = "\n".join(
        [
            f"### Decision: {decision}",
            "",
            "### Issues",
            *[f"- {issue}" for issue in issues],
            "",
            "### Suggested Fix",
            suggested_fix,
        ]
    )
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="continuity_check",
        answer_markdown=answer,
        evidence_or_source_policy=[
            CANON_POLICY,
            DRAFT_POLICY,
            DEPRECATED_POLICY,
            INSPIRATION_POLICY,
            NO_AUTO_CANON_POLICY,
        ],
        risks_or_limitations=[
            "This MVP checks governance policy only.",
            "It does not judge character behavior, tone, theme, or complex branch state.",
        ],
        suggested_next_step=suggested_fix,
        debug_task_plan=plan.to_dict(),
        provider=plan.provider,
    )
