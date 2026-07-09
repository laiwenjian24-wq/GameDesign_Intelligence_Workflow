"""Tests for the STUPID Narrative State Validation Layer."""

import json

from src.rules.continuity_rule_evaluator import (
    evaluate_continuity_rules,
    find_rule_evidence_gaps,
)
from src.workflows import continuity_checker


def _citation(text: str, source_file: str = "stupid_canon.md") -> dict:
    return {
        "source_file": source_file,
        "status": "canon",
        "summary": text,
        "excerpt": text,
        "reason_used": "status=canon",
    }


def _context(task: str, canon_texts=()) -> dict:
    return {
        "task_context": {"task": task},
        "canon_context": [_citation(text) for text in canon_texts],
        "deprecated_warnings": [],
        "draft_reference": [],
        "missing_evidence": [],
    }


def _identity_rule() -> dict:
    return {
        "id": "stupid.rin.identity",
        "enabled": True,
        "state_type": "character_state",
        "validation_type": "exclusive_value",
        "scope": {"type": "global", "value": "global"},
        "entity": "Rin",
        "attribute": "identity",
        "canon_value": "Nexus-7",
        "known_conflict_values": ["Nexus-6"],
        "evidence_keywords": {
            "task_any": ["identity", "model"],
            "canon_any": ["identity", "model"],
            "scope_any": [],
        },
        "risk_level": "高",
        "source": {"preferred_sources": ["character_canon.md"]},
    }


def _injury_rule(branch: str, canon_value: str, conflict_value: str) -> dict:
    branch_label = branch.replace("branch_", "Branch ").upper()
    return {
        "id": f"stupid.{branch}.rin.injury",
        "enabled": True,
        "state_type": "branch_state",
        "validation_type": "known_conflict",
        "scope": {"type": "branch", "value": branch},
        "entity": "Rin",
        "attribute": "injury_location",
        "canon_value": canon_value,
        "known_conflict_values": [conflict_value],
        "evidence_keywords": {
            "task_any": ["injury", "injured"],
            "canon_any": ["injury", "injured"],
            "scope_any": [branch_label],
        },
        "risk_level": "高",
        "source": {"preferred_sources": []},
    }


def test_correct_state_passes() -> None:
    context = _context(
        "Rin's identity is Nexus-7.",
        ["Rin's canon identity is Nexus-7."],
    )

    assert evaluate_continuity_rules(context, [_identity_rule()]) == []
    assert find_rule_evidence_gaps(context, [_identity_rule()]) == []


def test_known_conflict_is_reported() -> None:
    context = _context(
        "Rin's identity is Nexus-6.",
        ["Rin's canon identity is Nexus-7."],
    )

    conflicts = evaluate_continuity_rules(context, [_identity_rule()])

    assert len(conflicts) == 1
    assert conflicts[0]["validation_result"] == "conflict"
    assert conflicts[0]["task_value"] == "Nexus-6"
    assert conflicts[0]["canon_value"] == "Nexus-7"


def test_injury_conflict_is_reported() -> None:
    rule = _injury_rule("branch_a", "left leg", "right leg")
    context = _context(
        "In Branch A, Rin's right leg is injured.",
        ["Branch A canon: Rin's left leg injury is confirmed."],
    )

    conflicts = evaluate_continuity_rules(context, [rule])

    assert len(conflicts) == 1
    assert conflicts[0]["rule_id"] == "stupid.branch_a.rin.injury"


def test_branch_scope_isolation() -> None:
    rules = [
        _injury_rule("branch_a", "left leg", "right leg"),
        _injury_rule("branch_b", "right leg", "left leg"),
    ]

    explicit_a_with_only_b = _context(
        "In Branch A, Rin's right leg is injured.",
        ["Branch B canon: Rin's right leg injury is confirmed."],
    )
    assert evaluate_continuity_rules(explicit_a_with_only_b, rules) == []
    explicit_gaps = find_rule_evidence_gaps(explicit_a_with_only_b, rules)
    assert len(explicit_gaps) == 1
    assert explicit_gaps[0]["rule_id"] == "stupid.branch_a.rin.injury"
    assert explicit_gaps[0]["reason"] == "missing_canon"

    inferred_a = _context(
        "Rin's right leg is injured.",
        ["Branch A canon: Rin's left leg injury is confirmed."],
    )
    assert len(evaluate_continuity_rules(inferred_a, rules)) == 1

    ambiguous = _context(
        "Rin's right leg is injured.",
        [
            "Branch A canon: Rin's left leg injury is confirmed.",
            "Branch B canon: Rin's right leg injury is confirmed.",
        ],
    )
    assert evaluate_continuity_rules(ambiguous, rules) == []
    assert any(
        gap["reason"] == "ambiguous_branch"
        for gap in find_rule_evidence_gaps(ambiguous, rules)
    )


def test_missing_canon_returns_insufficient_evidence() -> None:
    context = _context("Rin's identity is Nexus-6.")

    gaps = find_rule_evidence_gaps(context, [_identity_rule()])

    assert len(gaps) == 1
    assert gaps[0]["validation_result"] == "insufficient_evidence"
    assert gaps[0]["reason"] == "missing_canon"


def test_unknown_value_returns_insufficient_evidence() -> None:
    context = _context(
        "Rin's identity is Nexus-8.",
        ["Rin's canon identity is Nexus-7."],
    )

    assert evaluate_continuity_rules(context, [_identity_rule()]) == []
    gaps = find_rule_evidence_gaps(context, [_identity_rule()])
    assert len(gaps) == 1
    assert gaps[0]["reason"] == "unknown_value"


def test_report_contract_remains_unchanged(tmp_path, monkeypatch) -> None:
    context = _context(
        "Rin's identity is Nexus-7.",
        ["Rin's canon identity is Nexus-7."],
    )
    monkeypatch.setattr(continuity_checker, "build_context_pack", lambda *args, **kwargs: context)
    rule_path = tmp_path / "rules.json"
    rule_path.write_text(json.dumps({"rules": [_identity_rule()]}), encoding="utf-8")

    report = continuity_checker.run_continuity_check(
        context["task_context"]["task"], tmp_path, rule_path=rule_path
    )

    assert set(report) == {
        "task",
        "risk_level",
        "canon_evidence",
        "deprecated_evidence",
        "draft_reference",
        "missing_evidence",
        "conflict_analysis",
        "final_decision",
        "rewrite_suggestion",
        "context_pack",
    }
    formatted = continuity_checker.format_continuity_report(report)
    for heading in (
        "## Task",
        "## Risk Level",
        "## Canon Evidence",
        "## Deprecated Evidence",
        "## Draft Reference",
        "## Missing Evidence",
        "## Conflict Analysis",
        "## Final Decision",
        "## Rewrite Suggestion",
    ):
        assert heading in formatted
