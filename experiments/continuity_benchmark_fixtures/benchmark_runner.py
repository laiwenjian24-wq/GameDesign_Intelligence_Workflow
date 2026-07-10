"""Run continuity benchmark fixtures against the isolated JSON checker."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.json_continuity_check_eval.check_continuity_from_json_pack import run_check  # noqa: E402

try:
    from .benchmark_schema import BenchmarkCase, BenchmarkResult
    from .report_writer import DEFAULT_REPORT_PATH, write_report
except ImportError:  # pragma: no cover - direct script execution
    from benchmark_schema import BenchmarkCase, BenchmarkResult
    from report_writer import DEFAULT_REPORT_PATH, write_report


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_FIXTURE_PATH = EXPERIMENT_DIR / "fixtures" / "continuity_cases.json"
DEFAULT_CONTEXT_PACK_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "normalized_context_schema"
    / "sample_outputs"
    / "context_pack.json"
)


def missing_context_pack_message(path: Path = DEFAULT_CONTEXT_PACK_PATH) -> str:
    return (
        f"JSON Context Pack not found: {path}\n"
        "Run the normalized_context_schema experiment first:\n"
        "E:\\Desktop\\python310\\python.exe experiments/normalized_context_schema/build_json_context_pack.py \"Rin是什么身份？\""
    )


def load_cases(path: Path = DEFAULT_FIXTURE_PATH) -> List[BenchmarkCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [BenchmarkCase.from_dict(item) for item in payload]


def load_context_pack(path: Path = DEFAULT_CONTEXT_PACK_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(missing_context_pack_message(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence_statuses_seen(result_payload: Dict[str, Any]) -> List[str]:
    statuses = set()
    for issue in result_payload.get("issues", []):
        for evidence in issue.get("related_evidence", []):
            status = evidence.get("status")
            if status:
                statuses.add(status)
    return sorted(statuses)


def _source_policy_notes(result_payload: Dict[str, Any]) -> List[str]:
    return [
        issue.get("source_policy", "")
        for issue in result_payload.get("issues", [])
        if issue.get("source_policy")
    ]


def _result_passed(case: BenchmarkCase, result_payload: Dict[str, Any]) -> tuple[bool, List[str]]:
    failure_reasons: List[str] = []
    actual_decision = result_payload.get("decision", "")
    actual_issue_types = [issue.get("issue_type", "") for issue in result_payload.get("issues", [])]
    source_policy_notes = _source_policy_notes(result_payload)

    if actual_decision not in case.allowed_decisions:
        failure_reasons.append(
            f"decision {actual_decision} not in allowed decisions {case.allowed_decisions}"
        )

    for issue_type in case.expected_issue_types:
        if issue_type not in actual_issue_types:
            failure_reasons.append(f"missing expected issue type: {issue_type}")

    if case.expected_source_policy:
        if not any(case.expected_source_policy in note or case.expected_source_policy == "insufficient" and "insufficient" in note.lower() for note in source_policy_notes):
            failure_reasons.append(f"missing expected source policy: {case.expected_source_policy}")

    statuses_seen = set(_evidence_statuses_seen(result_payload))
    if case.forbidden_evidence_statuses and actual_decision == "PASS" and statuses_seen.intersection(case.forbidden_evidence_statuses):
        failure_reasons.append(
            "case with forbidden evidence statuses must not pass as canon-supported"
        )

    return not failure_reasons, failure_reasons


def run_benchmark(cases: Iterable[BenchmarkCase], context_pack: Dict[str, Any]) -> List[BenchmarkResult]:
    results: List[BenchmarkResult] = []
    for case in cases:
        result_payload = run_check(case.input_text, context_pack)
        passed, failure_reasons = _result_passed(case, result_payload)
        actual_issue_types = [issue.get("issue_type", "") for issue in result_payload.get("issues", [])]
        results.append(
            BenchmarkResult(
                case_id=case.case_id,
                input_text=case.input_text,
                expected_decision=case.expected_decision,
                allowed_decisions=case.allowed_decisions,
                actual_decision=result_payload.get("decision", ""),
                passed=passed,
                expected_issue_types=case.expected_issue_types,
                actual_issue_types=actual_issue_types,
                notes=case.notes,
                failure_reasons=failure_reasons,
                source_policy_notes=_source_policy_notes(result_payload),
                evidence_statuses_seen=_evidence_statuses_seen(result_payload),
            )
        )
    return results


def run(
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    context_pack_path: Path = DEFAULT_CONTEXT_PACK_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> List[BenchmarkResult]:
    cases = load_cases(fixture_path)
    context_pack = load_context_pack(context_pack_path)
    results = run_benchmark(cases, context_pack)
    write_report(results, report_path)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run continuity benchmark fixtures.")
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--context-pack", type=Path, default=DEFAULT_CONTEXT_PACK_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    try:
        results = run(args.fixtures, args.context_pack, args.report)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    passed = sum(1 for result in results if result.passed)
    print(f"Continuity benchmark: {passed}/{len(results)} passed")
    print(f"Wrote report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
