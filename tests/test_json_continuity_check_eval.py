from experiments.json_continuity_check_eval.check_continuity_from_json_pack import (
    format_report,
    run_check,
)


def _evidence(status: str, text: str = "Rin is Nexus-7.", source: str = "source.md"):
    return {
        "evidence_id": f"{status}-0001",
        "source_file": source,
        "original_path": source,
        "status": status,
        "status_priority": "highest" if status == "canon" else "reference only",
        "section_title": "Section",
        "heading_path": ["Root", "Section"],
        "block_type": "text",
        "excerpt": text,
        "text": text,
        "source_ref": f"{source}::Section",
        "reason_used": "test evidence",
        "metadata": {"tags": [status]},
    }


def _pack(canon=None, draft=None, deprecated=None, inspiration=None):
    canon = canon or []
    draft = draft or []
    deprecated = deprecated or []
    inspiration = inspiration or []
    return {
        "query": "test",
        "canon_context": canon,
        "draft_reference": draft,
        "deprecated_warnings": deprecated,
        "inspiration_reference": inspiration,
        "missing_evidence": [],
        "source_summary": [],
        "diagnostics": {
            "source_count": 0,
            "evidence_count_by_status": {
                "canon": len(canon),
                "draft": len(draft),
                "deprecated": len(deprecated),
                "inspiration": len(inspiration),
            },
            "canon_count": len(canon),
            "draft_count": len(draft),
            "deprecated_count": len(deprecated),
            "inspiration_count": len(inspiration),
            "has_canon_evidence": bool(canon),
            "warnings": [],
        },
        "metadata": {},
    }


def test_no_canon_evidence_returns_missing_or_insufficient():
    result = run_check("Rin是Nexus-7仿生人。", _pack())
    issue_types = {issue["issue_type"] for issue in result["issues"]}

    assert issue_types & {"missing_canon_evidence", "insufficient_evidence"}
    assert result["decision"] == "NEEDS_REVIEW"


def test_deprecated_evidence_cannot_be_current_truth():
    result = run_check(
        "使用Deprecated资料作为当前事实。",
        _pack(canon=[_evidence("canon")], deprecated=[_evidence("deprecated", "old fact")]),
    )
    issue_types = {issue["issue_type"] for issue in result["issues"]}

    assert "deprecated_contamination" in issue_types
    assert result["decision"] == "FAIL"


def test_draft_cannot_override_canon():
    result = run_check(
        "草稿可以覆盖当前Canon。",
        _pack(canon=[_evidence("canon")], draft=[_evidence("draft", "draft fact")]),
    )
    issue_types = {issue["issue_type"] for issue in result["issues"]}

    assert "draft_overrides_canon" in issue_types
    assert result["decision"] == "FAIL"


def test_branch_conflict_uncertain_needs_review_or_insufficient():
    result = run_check(
        "Branch B中Rin右腿受伤。",
        _pack(canon=[_evidence("canon", "Rin is Nexus-7.")]),
    )
    issue_types = {issue["issue_type"] for issue in result["issues"]}

    assert issue_types & {"branch_state_conflict", "insufficient_evidence"}
    assert result["decision"] == "NEEDS_REVIEW"


def test_report_includes_source_policy():
    pack = _pack(canon=[_evidence("canon")], deprecated=[_evidence("deprecated")])
    result = run_check("使用Deprecated资料作为当前事实。", pack)
    report = format_report(result, pack)

    assert "source_policy" in report
    assert "Deprecated evidence" in report
