from src.v1.benchmark.benchmark_case import BenchmarkCase
from src.v1.benchmark.benchmark_result import BenchmarkResult


def test_benchmark_case_preserves_forbidden_evidence_statuses():
    case = BenchmarkCase(
        case_id="case-001",
        category="deprecated_override",
        input_text="旧版可以覆盖Canon。",
        expected_decision="FAIL",
        allowed_decisions=["FAIL"],
        expected_issue_types=["deprecated_contamination"],
        required_evidence_statuses=["canon"],
        forbidden_evidence_statuses=["deprecated", "draft", "inspiration"],
        notes="Governance regression case.",
    )

    assert case.forbidden_evidence_statuses == [
        "deprecated",
        "draft",
        "inspiration",
    ]
    assert case.to_dict()["case_id"] == "case-001"


def test_benchmark_result_can_be_created():
    result = BenchmarkResult(
        case_id="case-001",
        input_text="旧版可以覆盖Canon。",
        expected_decision="FAIL",
        actual_decision="FAIL",
        passed=True,
        expected_issue_types=["deprecated_contamination"],
        actual_issue_types=["deprecated_contamination"],
        notes="Passed governance check.",
    )

    assert result.passed is True
    assert result.to_dict()["actual_decision"] == "FAIL"
