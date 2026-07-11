from src.v1.chat.response_models import TaskPlan
from src.v1.tasks import llm_backend
from src.v1.tasks.continuity_check import detect_canon_conflict, run_continuity_check_task


def _canon_left_leg_evidence():
    return {
        "source_file": "时间线.md",
        "status": "canon",
        "section_title": "第九章 — 风筝（鼠、Rin）",
        "excerpt": "鼠右肩负伤，Rin左腿被流弹擦伤。",
        "reason_used": "matched:Rin, matched:Branch B",
        "score": 20,
    }


def _plan(evidence):
    return TaskPlan(
        task_type="continuity_check",
        user_intent="Branch B中Rin右腿受伤，这样能用吗？",
        entities=["Rin"],
        branch_scope="Branch B",
        provider="deepseek",
        metadata={"lite_evidence": evidence, "kb_path": "processed/v1_lite_kb.json"},
    )


def test_right_leg_claim_left_leg_canon_conflict_finding_fail():
    pack = {
        "canon": [_canon_left_leg_evidence()],
        "draft": [],
        "deprecated": [],
        "inspiration": [],
        "unknown": [],
    }

    finding = detect_canon_conflict("Branch B中Rin右腿受伤，这样能用吗？", pack)

    assert finding.has_conflict is True
    assert finding.decision == "FAIL"
    assert finding.conflict_type == "injury_side_conflict"
    assert "左腿" in finding.canonical_fact
    assert "右腿" in finding.user_claim


def test_mocked_deepseek_needs_review_cannot_override_locked_fail(monkeypatch):
    monkeypatch.setattr(
        llm_backend,
        "generate_with_deepseek",
        lambda **_kwargs: llm_backend.LLMResult(
            ok=True,
            text="### Decision\nNEEDS_REVIEW\n\nMissing reliable evidence.",
        ),
    )

    response = run_continuity_check_task(
        "Branch B中Rin右腿受伤，这样能用吗？",
        _plan([_canon_left_leg_evidence()]),
    )

    assert "### Decision: FAIL" in response.answer_markdown
    assert "NEEDS_REVIEW" not in response.answer_markdown
    assert "左腿" in response.answer_markdown


def test_mocked_deepseek_empty_output_falls_back_to_locked_fail(monkeypatch):
    monkeypatch.setattr(
        llm_backend,
        "generate_with_deepseek",
        lambda **_kwargs: llm_backend.LLMResult(ok=True, text=""),
    )

    response = run_continuity_check_task(
        "Branch B中Rin右腿受伤，这样能用吗？",
        _plan([_canon_left_leg_evidence()]),
    )

    assert "### Decision: FAIL" in response.answer_markdown
    assert "Missing reliable LLM output" not in response.answer_markdown
    assert "Suggested Fix" in response.answer_markdown


def test_locked_conflict_suggested_fix_contains_left_leg(monkeypatch):
    monkeypatch.setattr(
        llm_backend,
        "generate_with_deepseek",
        lambda **_kwargs: llm_backend.LLMResult(ok=False, text="", fallback_reason="mock failure"),
    )

    response = run_continuity_check_task(
        "Branch B中Rin右腿受伤，这样能用吗？",
        _plan([_canon_left_leg_evidence()]),
    )

    assert "将右腿改为左腿" in response.answer_markdown


def test_no_left_leg_canon_evidence_can_remain_needs_review(monkeypatch):
    monkeypatch.setattr(
        llm_backend,
        "generate_with_deepseek",
        lambda **_kwargs: llm_backend.LLMResult(
            ok=True,
            text="### Decision\nNEEDS_REVIEW\n\nNo wound-side canon evidence.",
        ),
    )
    evidence = [
        {
            "source_file": "branch.md",
            "status": "canon",
            "section_title": "Branch B",
            "excerpt": "Branch B safehouse scene.",
            "reason_used": "matched:Branch B",
            "score": 10,
        }
    ]

    response = run_continuity_check_task(
        "Branch B中Rin右腿受伤，这样能用吗？",
        _plan(evidence),
    )

    assert "NEEDS_REVIEW" in response.answer_markdown
