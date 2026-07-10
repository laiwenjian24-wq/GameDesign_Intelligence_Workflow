"""Canon QA task for the Daily Narrative Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import (
    CANON_POLICY,
    DEPRECATED_POLICY,
    DRAFT_POLICY,
    INSPIRATION_POLICY,
    NO_AUTO_CANON_POLICY,
)
from src.v1.tasks import llm_backend


def run_canon_qa(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    lite_evidence = plan.metadata.get("lite_evidence", [])
    if plan.provider == "deepseek":
        try:
            return _run_deepseek_canon_qa(user_request, plan)
        except Exception as exc:
            fallback_plan = TaskPlan(**plan.to_dict())
            fallback_plan.provider = "fake"
            fallback_plan.fallback_reason = f"deepseek_task_failed: {exc}"
            response = run_canon_qa(user_request, fallback_plan)
            response.metadata["fallback_reason"] = fallback_plan.fallback_reason
            response.debug_task_plan = fallback_plan.to_dict()
            return response

    if lite_evidence:
        canon = [item for item in lite_evidence if item.get("status") == "canon"]
        if not canon:
            answer = (
                "### Decision: NEEDS_REVIEW\n\n"
                "Lite KB retrieved evidence, but no Canon evidence was available.\n\n"
                "### Evidence Snippets\n"
                + llm_backend.evidence_snippet_markdown(lite_evidence)
            )
            next_step = "Add or retrieve reviewed Canon evidence before answering as current truth."
        else:
            answer = (
                "### Evidence-backed Canon QA Draft\n\n"
                "The Lite KB retrieved Canon evidence candidates. Treat this as a grounded draft, not automatic Canon.\n\n"
                "### Evidence Snippets\n"
                + llm_backend.evidence_snippet_markdown(canon)
            )
            next_step = "Review the cited Canon snippets and then write the final answer."
    elif "Rin" in user_request and ("身份" in user_request or "是什么" in user_request):
        answer = (
            "MVP demo answer: Rin should be handled as a Canon-evidence-backed "
            "character identity question. The fake provider does not claim final "
            "research; it asks the user to retrieve Canon identity evidence before "
            "using the answer as production truth."
        )
        next_step = "Use v0.4 `ask-rag` or the v1 JSON Context Pack path to retrieve Rin Canon identity evidence."
    else:
        answer = "Missing Evidence / Needs Review: fake provider has no deterministic rule for this setting question."
        next_step = "Add or retrieve Canon evidence, or use opt-in DeepSeek for assisted review."
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


def _run_deepseek_canon_qa(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    lite_evidence = plan.metadata.get("lite_evidence", [])
    if lite_evidence:
        context_pack = llm_backend.context_pack_from_lite_evidence(lite_evidence)
        warnings = []
    else:
        context_pack, warnings = llm_backend.build_retrieval_context(user_request)
    if not llm_backend.has_canon_evidence(context_pack):
        payload = llm_backend.missing_evidence_payload(
            "No Canon evidence was retrieved for this Canon QA request."
        )
    else:
        payload = llm_backend.call_deepseek_markdown(
            "canon_qa",
            user_request,
            context_pack,
            "Answer the setting question with Canon citations and Missing Evidence when needed.",
        )
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="canon_qa",
        answer_markdown=payload["answer_markdown"] or "Missing Evidence / NEEDS_REVIEW.",
        evidence_or_source_policy=llm_backend.source_policy_lines(),
        risks_or_limitations=payload["risks_or_limitations"] + warnings,
        suggested_next_step=payload["suggested_next_step"]
        or "Review cited Canon sources before using this as production truth.",
        debug_task_plan=plan.to_dict(),
        provider="deepseek",
        metadata={"retrieval_warnings": warnings, "llm_payload": payload.get("raw_payload", {})},
    )
