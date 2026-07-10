"""Art prompt brief task for the Daily Narrative Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import CANON_POLICY, INSPIRATION_POLICY, NO_AUTO_CANON_POLICY
from src.v1.tasks import llm_backend


def run_art_prompt(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    lite_evidence = plan.metadata.get("lite_evidence", [])
    if plan.provider == "deepseek":
        try:
            return _run_deepseek_art_prompt(user_request, plan)
        except Exception as exc:
            fallback_plan = TaskPlan(**plan.to_dict())
            fallback_plan.provider = "fake"
            fallback_plan.fallback_reason = f"deepseek_task_failed: {exc}"
            response = run_art_prompt(user_request, fallback_plan)
            response.metadata["fallback_reason"] = fallback_plan.fallback_reason
            response.debug_task_plan = fallback_plan.to_dict()
            return response

    branch = plan.branch_scope or "Branch scope needs confirmation"
    evidence_note = (
        "\n### Retrieved Source Context\n" + llm_backend.evidence_snippet_markdown(lite_evidence)
        if lite_evidence
        else ""
    )
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
{evidence_note}

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


def _run_deepseek_art_prompt(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    lite_evidence = plan.metadata.get("lite_evidence", [])
    if lite_evidence:
        context_pack = llm_backend.context_pack_from_lite_evidence(lite_evidence)
        warnings = []
    else:
        context_pack, warnings = llm_backend.build_retrieval_context(user_request)
    if not llm_backend.has_canon_evidence(context_pack):
        payload = llm_backend.missing_evidence_payload(
            "No Canon or visual evidence was retrieved for this art prompt brief."
        )
    else:
        payload = llm_backend.call_deepseek_markdown(
            "art_prompt",
            user_request,
            context_pack,
            "Generate Production Prompt / Continuity Checklist / Negative Constraints / Source Needs. Do not generate an image.",
        )
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="art_prompt",
        answer_markdown=payload["answer_markdown"] or "Missing Evidence / NEEDS_REVIEW.",
        evidence_or_source_policy=llm_backend.source_policy_lines()
        + ["This task outputs a prompt brief only; it does not generate images."],
        risks_or_limitations=payload["risks_or_limitations"] + warnings,
        suggested_next_step=payload["suggested_next_step"]
        or "Attach Canon visual references before sending this to an image pipeline.",
        debug_task_plan=plan.to_dict(),
        provider="deepseek",
        metadata={"retrieval_warnings": warnings, "llm_payload": payload.get("raw_payload", {})},
    )
