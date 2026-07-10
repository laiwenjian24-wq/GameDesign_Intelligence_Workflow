import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "v1" / "continuity_cases.json"
REQUIRED_FIELDS = {
    "case_id",
    "category",
    "input_text",
    "expected_issue_types",
    "required_evidence_statuses",
    "forbidden_evidence_statuses",
    "notes",
}
REQUIRED_CATEGORIES = {
    "canon_supported_fact",
    "unsupported_identity_claim",
    "branch_state_uncertain",
    "deprecated_override",
    "deprecated_current_truth",
    "draft_override",
    "missing_canon_evidence",
    "inspiration_as_fact",
}
ALLOWED_FORBIDDEN_STATUSES = {"draft", "deprecated", "inspiration", "unknown"}


def _load_cases():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_v1_continuity_fixture_file_exists():
    assert FIXTURE_PATH.exists()


def test_v1_continuity_fixtures_load_as_json():
    cases = _load_cases()

    assert isinstance(cases, list)
    assert cases


def test_v1_continuity_fixtures_have_required_fields():
    for case in _load_cases():
        assert REQUIRED_FIELDS.issubset(case)
        assert "expected_decision" in case or "allowed_decisions" in case


def test_v1_continuity_fixture_case_ids_are_unique():
    case_ids = [case["case_id"] for case in _load_cases()]

    assert len(case_ids) == len(set(case_ids))


def test_v1_continuity_fixtures_cover_required_categories():
    categories = {case["category"] for case in _load_cases()}

    assert REQUIRED_CATEGORIES.issubset(categories)


def test_v1_continuity_forbidden_statuses_are_limited_to_non_canon():
    for case in _load_cases():
        forbidden = set(case["forbidden_evidence_statuses"])
        assert forbidden.issubset(ALLOWED_FORBIDDEN_STATUSES)


def test_deprecated_cases_forbid_deprecated_evidence_as_support():
    for case in _load_cases():
        if case["category"] in {"deprecated_current_truth", "deprecated_override"}:
            assert "deprecated" in case["forbidden_evidence_statuses"]


def test_draft_override_cases_forbid_draft_evidence_as_support():
    for case in _load_cases():
        if case["category"] == "draft_override":
            assert "draft" in case["forbidden_evidence_statuses"]


def test_inspiration_as_fact_cases_forbid_inspiration_evidence_as_support():
    for case in _load_cases():
        if case["category"] == "inspiration_as_fact":
            assert "inspiration" in case["forbidden_evidence_statuses"]
