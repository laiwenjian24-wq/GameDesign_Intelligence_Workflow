"""Minimal governance continuity check task for the Daily Assistant MVP."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import (
    CANON_POLICY,
    DEPRECATED_POLICY,
    DRAFT_POLICY,
    INSPIRATION_POLICY,
    NO_AUTO_CANON_POLICY,
)
from src.v1.tasks import llm_backend


def run_continuity_check_task(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    lite_evidence = plan.metadata.get("lite_evidence", [])
    if plan.provider == "deepseek":
        try:
            return _run_deepseek_continuity_check(user_request, plan)
        except Exception as exc:
            fallback_plan = TaskPlan(**plan.to_dict())
            fallback_plan.provider = "fake"
            fallback_plan.fallback_reason = f"deepseek_task_failed: {exc}"
            response = run_continuity_check_task(user_request, fallback_plan)
            response.metadata["fallback_reason"] = fallback_plan.fallback_reason
            response.debug_task_plan = fallback_plan.to_dict()
            return response

    decision = "NEEDS_REVIEW"
    issues = []
    suggested_fix = "Retrieve branch-specific Canon evidence before accepting this content."

    if any(term in user_request for term in ("Deprecated", "deprecated", "废弃", "旧版", "覆盖当前Canon")):
        decision = "FAIL"
        issues.append("Deprecated material cannot be used as current truth or override Canon.")
        suggested_fix = "Keep deprecated material as conflict history only."
    if any(term in user_request for term in ("草稿", "Draft", "draft")) and "覆盖" in user_request:
        decision = "FAIL"
        issues.append("Draft material cannot override Canon.")
        suggested_fix = "Use human canonization review before promoting draft material."
    if "灵感" in user_request and ("事实" in user_request or "当前" in user_request):
        decision = "FAIL"
        issues.append("Inspiration cannot be used as factual evidence.")
        suggested_fix = "Use inspiration as thematic reference only."
    if not issues:
        issues.append("Canon evidence is required; this MVP does not perform full semantic verification.")

    evidence_section = ""
    if lite_evidence:
        evidence_section = "\n\n### Evidence Snippets\n" + llm_backend.evidence_snippet_markdown(lite_evidence)

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
    ) + evidence_section
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


def _governance_blocking_issue(user_request: str) -> str:
    if any(term in user_request for term in ("Deprecated", "deprecated", "废弃", "旧版")) and any(
        term in user_request for term in ("当前事实", "覆盖", "current truth")
    ):
        return "Deprecated material cannot be used as current truth or override Canon."
    if any(term in user_request for term in ("Draft", "draft", "草稿")) and "覆盖" in user_request:
        return "Draft material cannot override Canon."
    if "灵感" in user_request and any(term in user_request for term in ("事实", "当前")):
        return "Inspiration cannot be used as factual evidence."
    return ""


def _run_deepseek_continuity_check(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    blocking_issue = _governance_blocking_issue(user_request)
    lite_evidence = plan.metadata.get("lite_evidence", [])
    if lite_evidence:
        context_pack = llm_backend.context_pack_from_lite_evidence(lite_evidence)
        warnings = []
    else:
        context_pack, warnings = llm_backend.build_retrieval_context(user_request)
    if blocking_issue:
        answer = "\n".join(
            [
                "### Decision: FAIL",
                "",
                "### Issues",
                f"- {blocking_issue}",
                "",
                "### Suggested Fix",
                "Keep non-Canon material out of current-truth decisions and use human canonization review.",
            ]
        )
        risks = ["Governance policy blocked this claim before semantic judgment."] + warnings
    elif not llm_backend.has_canon_evidence(context_pack):
        payload = llm_backend.missing_evidence_payload(
            "No Canon evidence was retrieved for this continuity check."
        )
        answer = payload["answer_markdown"]
        risks = payload["risks_or_limitations"] + warnings
    else:
        payload = llm_backend.call_deepseek_markdown(
            "continuity_check",
            user_request,
            context_pack,
            "Extract the claim, then output Decision / Issues / Suggested Fix. Never allow Draft, Deprecated, or Inspiration as current truth.",
        )
        answer = payload["answer_markdown"] or "### Decision: NEEDS_REVIEW\n\nMissing reliable LLM output."
        risks = payload["risks_or_limitations"] + warnings
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="continuity_check",
        answer_markdown=answer,
        evidence_or_source_policy=llm_backend.source_policy_lines(),
        risks_or_limitations=risks,
        suggested_next_step="Review Canon evidence and keep non-Canon material out of current-truth decisions.",
        debug_task_plan=plan.to_dict(),
        provider="deepseek",
        metadata={"retrieval_warnings": warnings},
    )
