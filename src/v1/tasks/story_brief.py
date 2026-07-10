"""Story brief task for the Daily Narrative Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import CANON_POLICY, NO_AUTO_CANON_POLICY
from src.v1.tasks import llm_backend


def run_story_brief(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    if plan.provider == "deepseek":
        try:
            return _run_deepseek_story_brief(user_request, plan)
        except Exception as exc:
            fallback_plan = TaskPlan(**plan.to_dict())
            fallback_plan.provider = "fake"
            fallback_plan.fallback_reason = f"deepseek_task_failed: {exc}"
            response = run_story_brief(user_request, fallback_plan)
            response.metadata["fallback_reason"] = fallback_plan.fallback_reason
            response.debug_task_plan = fallback_plan.to_dict()
            return response

    constraints = ", ".join(plan.constraints) if plan.constraints else "restrained, source-grounded"
    answer = f"""### Scene Goal
Clarify the next playable/narrative beat without changing Canon.

### Required Context
- Location: Mombasa safehouse if supported by Canon evidence.
- Characters: {", ".join(plan.entities) or "Mouse and Rin if confirmed by source context"}.
- Branch scope: {plan.branch_scope or "Needs confirmation"}.

### Character Constraints
- Keep the tone restrained.
- Avoid sudden confession or exaggerated intimacy.
- Do not introduce new Canon facts.
- User constraints: {constraints}.

### Draft Beat
1. Open with practical wound-care or equipment maintenance.
2. Let silence and small actions carry trust.
3. End on an unresolved but playable next decision.

### Risks / Continuity Notes
- Needs Canon confirmation for wound state, branch state, and room/location details.

### Suggested Next Step
Turn this brief into a scene-function card before drafting dialogue.
"""
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="story_brief",
        answer_markdown=answer,
        evidence_or_source_policy=[CANON_POLICY, NO_AUTO_CANON_POLICY],
        risks_or_limitations=[
            "This is a scene brief, not a full script.",
            "Human review is required before treating any new detail as Canon.",
        ],
        suggested_next_step="Create a Scene Function Registry entry for this scene.",
        debug_task_plan=plan.to_dict(),
        provider=plan.provider,
    )


def _run_deepseek_story_brief(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    context_pack, warnings = llm_backend.build_retrieval_context(user_request)
    if not llm_backend.has_canon_evidence(context_pack):
        payload = llm_backend.missing_evidence_payload(
            "No Canon evidence was retrieved for this story brief."
        )
    else:
        payload = llm_backend.call_deepseek_markdown(
            "story_brief",
            user_request,
            context_pack,
            "Generate Scene Goal / Required Context / Character Constraints / Draft Beat / Risks. Do not write a full script.",
        )
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="story_brief",
        answer_markdown=payload["answer_markdown"] or "Missing Evidence / NEEDS_REVIEW.",
        evidence_or_source_policy=llm_backend.source_policy_lines(),
        risks_or_limitations=payload["risks_or_limitations"] + warnings,
        suggested_next_step=payload["suggested_next_step"]
        or "Turn this into a Scene Function Registry entry after human review.",
        debug_task_plan=plan.to_dict(),
        provider="deepseek",
        metadata={"retrieval_warnings": warnings, "llm_payload": payload.get("raw_payload", {})},
    )
