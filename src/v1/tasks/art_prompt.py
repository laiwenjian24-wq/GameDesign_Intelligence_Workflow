"""Art prompt brief task for the Daily Narrative Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import CANON_POLICY, INSPIRATION_POLICY, NO_AUTO_CANON_POLICY


def run_art_prompt(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    branch = plan.branch_scope or "Branch scope needs confirmation"
    answer = f"""### Production Prompt
Branch B mutual bandaging scene, restrained trust, practical wound care, safehouse interior, quiet tension, cinematic visual novel CG composition, grounded cyberpunk materials, no melodramatic romance.

### Continuity Checklist
- Branch: {branch}
- Confirm Mouse/Rin wound states from Canon evidence.
- Preserve reciprocal care and restraint.
- Keep costumes, props, and room layout source-grounded.

### Negative Constraints
- No sudden confession.
- No exaggerated intimacy.
- No unsupported injury side.
- No Deprecated or Draft-only details as current fact.

### Source Needs
- Visual Bible / CG mapping evidence.
- Branch B scene state.
- Character appearance constraints.

### Suggested Next Step
Attach Canon visual references before sending this to an image pipeline.
"""
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="art_prompt",
        answer_markdown=answer,
        evidence_or_source_policy=[
            CANON_POLICY,
            INSPIRATION_POLICY,
            NO_AUTO_CANON_POLICY,
            "This task outputs a prompt brief only; it does not generate images.",
        ],
        risks_or_limitations=[
            "No ComfyUI / InvokeAI integration is used.",
            "Prompt must be checked against Canon visual constraints.",
        ],
        suggested_next_step="Collect Canon visual references and turn this into a production prompt sheet.",
        debug_task_plan=plan.to_dict(),
        provider=plan.provider,
    )
