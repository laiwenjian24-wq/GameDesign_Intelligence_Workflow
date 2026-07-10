"""Story brief task for the Daily Narrative Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import CANON_POLICY, NO_AUTO_CANON_POLICY


def run_story_brief(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
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
