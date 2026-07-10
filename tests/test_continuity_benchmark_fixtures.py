import json
from pathlib import Path

from experiments.continuity_benchmark_fixtures.benchmark_runner import (
    DEFAULT_FIXTURE_PATH,
    load_cases,
    run_benchmark,
)
from experiments.continuity_benchmark_fixtures.report_writer import render_report


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


def _sample_pack():
    return {
        "query": "test",
        "canon_context": [_evidence("canon", "Rin is Nexus-7 仿生人.")],
        "draft_reference": [_evidence("draft", "draft")],
        "deprecated_warnings": [_evidence("deprecated", "deprecated")],
        "inspiration_reference": [_evidence("inspiration", "inspiration")],
        "missing_evidence": [],
        "source_summary": [],
        "diagnostics": {
            "source_count": 4,
            "evidence_count_by_status": {
                "canon": 1,
                "draft": 1,
                "deprecated": 1,
                "inspiration": 1,
            },
            "canon_count": 1,
            "draft_count": 1,
            "deprecated_count": 1,
            "inspiration_count": 1,
            "has_canon_evidence": True,
            "warnings": [],
        },
        "metadata": {},
    }


def test_fixture_json_loads():
    payload = json.loads(DEFAULT_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert payload
    assert isinstance(payload, list)


def test_each_fixture_has_required_fields():
    required = {
        "case_id",
        "category",
        "input_text",
        "expected_decision",
        "expected_issue_types",
        "required_evidence_statuses",
        "forbidden_evidence_statuses",
        "expected_source_policy",
        "notes",
    }
    payload = json.loads(DEFAULT_FIXTURE_PATH.read_text(encoding="utf-8"))

    for item in payload:
        assert required.issubset(item)


def test_benchmark_runner_runs_with_sample_context_pack():
    cases = load_cases()

    results = run_benchmark(cases, _sample_pack())

    assert len(results) == len(cases)
    assert all(result.actual_decision for result in results)


def test_forbidden_evidence_status_cases_do_not_pass_as_canon_supported():
    cases = [
        case
        for case in load_cases()
        if {"draft", "deprecated", "inspiration"} & set(case.forbidden_evidence_statuses)
    ]

    results = run_benchmark(cases, _sample_pack())

    for result in results:
        assert not (result.actual_decision == "PASS" and result.passed)


def test_report_writer_outputs_pass_rate():
    results = run_benchmark(load_cases()[:2], _sample_pack())

    report = render_report(results)

    assert "pass rate" in report
    assert "total cases" in report
