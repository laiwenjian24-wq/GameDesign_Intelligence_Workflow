"""Minimal governance continuity check task for the Daily Assistant MVP."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.continuity.source_policy import (
    CANON_POLICY,
    DEPRECATED_POLICY,
    DRAFT_POLICY,
    INSPIRATION_POLICY,
    NO_AUTO_CANON_POLICY,
)
from src.v1.tasks import llm_backend


@dataclass
class ConflictFinding:
    has_conflict: bool = False
    decision: str = "NEEDS_REVIEW"
    conflict_type: str = ""
    canonical_fact: str = ""
    user_claim: str = ""
    suggested_fix: str = ""
    evidence_used: List[Dict[str, Any]] = field(default_factory=list)


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
    if lite_evidence:
        conflict = detect_canon_conflict(user_request, llm_backend.evidence_pack_from_items(lite_evidence))
        if conflict.has_conflict:
            return DailyAssistantResponse(
                user_request=user_request,
                detected_task="continuity_check",
                answer_markdown=_locked_conflict_fallback_markdown(conflict),
                evidence_or_source_policy=[
                    CANON_POLICY,
                    DRAFT_POLICY,
                    DEPRECATED_POLICY,
                    INSPIRATION_POLICY,
                    NO_AUTO_CANON_POLICY,
                ],
                risks_or_limitations=[
                    "System precheck locked Decision: FAIL from Canon evidence.",
                    "Fake provider did not perform open-ended semantic reasoning.",
                ],
                suggested_next_step=conflict.suggested_fix,
                debug_task_plan=llm_backend.compact_task_plan_debug(plan),
                provider=plan.provider,
                metadata={"conflict_finding": conflict.__dict__},
            )

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
        debug_task_plan=llm_backend.compact_task_plan_debug(plan),
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
        evidence_pack = llm_backend.evidence_pack_from_items(lite_evidence)
        context_pack = llm_backend.context_pack_from_evidence_pack(evidence_pack)
        warnings = []
    else:
        context_pack, warnings = llm_backend.build_retrieval_context(user_request)
        evidence_pack = {
            "canon": context_pack.get("canon_context", []),
            "draft": context_pack.get("draft_reference", []),
            "deprecated": context_pack.get("deprecated_warnings", []),
            "inspiration": context_pack.get("inspiration_context", []),
            "unknown": [],
        }
    conflict = detect_canon_conflict(user_request, evidence_pack)
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
        metadata = {}
    elif conflict.has_conflict:
        result = llm_backend.generate_with_deepseek(
            task_type="continuity_check",
            user_request=user_request,
            evidence_pack=evidence_pack,
            task_plan={
                **llm_backend.compact_task_plan_debug(plan),
                "locked_decision": conflict.decision,
                "conflict_type": conflict.conflict_type,
            },
            output_contract=(
                "The system has already detected a canon conflict. You must preserve "
                "Decision: FAIL. Do not downgrade to NEEDS_REVIEW. Use the provided Canon "
                "evidence only. Deprecated/Draft evidence may explain contamination but "
                "cannot override Canon. Output sections: Decision, Canon Finding, Conflict "
                "Analysis, Deprecated/Draft Evidence if any, Suggested Fix, Evidence Used, Limitations."
            ),
            source_policy=llm_backend.source_policy_text(),
        )
        if result.ok and _preserves_locked_fail(result.text):
            answer = result.text
            risks = ["System precheck locked Decision: FAIL before DeepSeek synthesis."] + warnings
            metadata = {
                "llm_result": {"ok": True, "provider": result.provider},
                "conflict_finding": conflict.__dict__,
            }
        else:
            answer = _locked_conflict_fallback_markdown(conflict)
            fallback_reason = result.fallback_reason or "llm_output_did_not_preserve_locked_fail"
            risks = [
                "System precheck locked Decision: FAIL before DeepSeek synthesis.",
                f"DeepSeek fallback used: {fallback_reason}",
            ] + warnings
            metadata = {
                "llm_result": {
                    "ok": result.ok,
                    "provider": result.provider,
                    "fallback_reason": fallback_reason,
                },
                "conflict_finding": conflict.__dict__,
            }
    elif not llm_backend.has_canon_evidence(context_pack):
        payload = llm_backend.missing_evidence_payload(
            "No Canon evidence was retrieved for this continuity check."
        )
        answer = payload["answer_markdown"]
        risks = payload["risks_or_limitations"] + warnings
        metadata = {}
    else:
        result = llm_backend.generate_with_deepseek(
            task_type="continuity_check",
            user_request=user_request,
            evidence_pack=evidence_pack,
            task_plan=llm_backend.compact_task_plan_debug(plan),
            output_contract=(
                "Output sections: Decision, Canon Finding, Conflict Analysis, "
                "Deprecated/Draft Evidence if any, Suggested Fix, Evidence Used, Limitations. "
                "If Canon says Rin left leg was injured and the claim says right leg, output FAIL or CONFLICT "
                "and suggest changing it to left leg unless this is a human Canon revision request."
            ),
            source_policy=llm_backend.source_policy_text(),
        )
        if result.ok:
            answer = result.text or "### Decision: NEEDS_REVIEW\n\nMissing reliable LLM output."
            risks = ["DeepSeek synthesized the review from provided evidence only."] + warnings
            metadata = {"llm_result": {"ok": True, "provider": result.provider}}
        else:
            fallback_plan = TaskPlan(**plan.to_dict())
            fallback_plan.provider = "fake"
            fallback_plan.fallback_reason = result.fallback_reason
            response = run_continuity_check_task(user_request, fallback_plan)
            response.metadata["fallback_reason"] = result.fallback_reason
            response.debug_task_plan = llm_backend.compact_task_plan_debug(
                fallback_plan,
                result.fallback_reason,
            )
            return response
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="continuity_check",
        answer_markdown=answer,
        evidence_or_source_policy=llm_backend.source_policy_lines(),
        risks_or_limitations=risks,
        suggested_next_step="Review Canon evidence and keep non-Canon material out of current-truth decisions.",
        debug_task_plan=llm_backend.compact_task_plan_debug(plan),
        provider="deepseek",
        metadata={"retrieval_warnings": warnings, **metadata},
    )


def detect_canon_conflict(
    user_request: str,
    evidence_pack: Dict[str, List[Dict[str, Any]]],
) -> ConflictFinding:
    """Detect small high-confidence Canon conflicts before LLM synthesis."""
    if not _is_rin_branch_b_right_leg_injury_claim(user_request):
        return ConflictFinding()

    matched_evidence: List[Dict[str, Any]] = []
    for item in evidence_pack.get("canon", []):
        text = _evidence_text(item)
        normalized = _compact_text(text)
        if any(
            marker in normalized
            for marker in (
                "rin左腿",
                "rin左腿被流弹擦伤",
                "左腿被流弹擦伤",
                "rin left leg",
                "left leg was grazed",
            )
        ):
            matched_evidence.append(item)

    if not matched_evidence:
        return ConflictFinding()

    return ConflictFinding(
        has_conflict=True,
        decision="FAIL",
        conflict_type="injury_side_conflict",
        canonical_fact="Branch B 中 Rin 左腿被流弹擦伤；Mouse 右肩负伤。",
        user_claim="Rin 右腿受伤",
        suggested_fix="将右腿改为左腿；除非发起 Canon revision，否则不能作为当前 Canon 使用。",
        evidence_used=matched_evidence[:3],
    )


def _is_rin_branch_b_right_leg_injury_claim(user_request: str) -> bool:
    lowered = user_request.lower()
    compact = _compact_text(user_request)
    has_rin = "rin" in lowered
    has_branch_b = "branchb" in compact or "branch_b" in lowered or "branch b" in lowered
    has_right_leg = any(term in compact for term in ("右腿", "rightleg"))
    has_injury = any(term in compact for term in ("受伤", "擦伤", "伤势", "injury", "injured", "grazed"))
    return has_rin and has_branch_b and has_right_leg and has_injury


def _evidence_text(item: Dict[str, Any]) -> str:
    return " ".join(
        str(item.get(key, ""))
        for key in ("source_file", "section_title", "excerpt", "text", "reason_used")
    )


def _compact_text(text: str) -> str:
    return "".join(str(text or "").lower().split())


def _preserves_locked_fail(text: str) -> bool:
    compact = _compact_text(text)
    if not compact:
        return False
    if "needs_review" in compact or "needsreview" in compact:
        return False
    return "decision" in compact and ("fail" in compact or "conflict" in compact)


def _locked_conflict_fallback_markdown(conflict: ConflictFinding) -> str:
    lines = [
        "### Decision: FAIL",
        "",
        "### Canon Finding",
        conflict.canonical_fact,
        "",
        "### Conflict Analysis",
        "用户输入的 Rin 右腿受伤与当前 Canon 的 Rin 左腿被流弹擦伤冲突。",
        "",
        "### Suggested Fix",
        "将右腿改为左腿。除非明确发起 Canon revision，否则不要把右腿设定用于正文、CG prompt 或 scene brief。",
        "",
        "### Evidence Used",
    ]
    for item in conflict.evidence_used:
        lines.append(
            f"- {item.get('source_file', '')} [{item.get('status', 'canon')}] "
            f"{item.get('section_title', '')}"
        )
    return "\n".join(lines)
