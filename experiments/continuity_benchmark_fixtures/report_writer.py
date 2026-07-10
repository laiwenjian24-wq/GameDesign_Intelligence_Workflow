"""Write continuity benchmark reports."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

try:
    from .benchmark_schema import BenchmarkResult
except ImportError:  # pragma: no cover - direct script execution
    from benchmark_schema import BenchmarkResult


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parent
    / "sample_outputs"
    / "continuity_benchmark_report.md"
)


def render_report(results: Iterable[BenchmarkResult]) -> str:
    result_list = list(results)
    total = len(result_list)
    passed = sum(1 for result in result_list if result.passed)
    failed = total - passed
    pass_rate = (passed / total * 100) if total else 0.0

    lines: List[str] = [
        "# Continuity Benchmark Report",
        "",
        "## Summary",
        "",
        f"- total cases: {total}",
        f"- passed count: {passed}",
        f"- failed count: {failed}",
        f"- pass rate: {pass_rate:.1f}%",
        "",
        "## Case Table",
        "",
        "| Case | Expected | Actual | Passed | Expected Issues | Actual Issues |",
        "|---|---|---|---|---|---|",
    ]
    for result in result_list:
        lines.append(
            "| "
            f"{result.case_id} | "
            f"{result.expected_decision} | "
            f"{result.actual_decision} | "
            f"{'yes' if result.passed else 'no'} | "
            f"{', '.join(result.expected_issue_types) or 'None'} | "
            f"{', '.join(result.actual_issue_types) or 'None'} |"
        )

    lines.extend(["", "## Failure Analysis", ""])
    failures = [result for result in result_list if not result.passed]
    if not failures:
        lines.append("- None")
    else:
        for result in failures:
            lines.append(f"### {result.case_id}")
            for reason in result.failure_reasons:
                lines.append(f"- {reason}")

    lines.extend(["", "## Source Policy Notes", ""])
    any_policy = False
    for result in result_list:
        if result.source_policy_notes:
            any_policy = True
            lines.append(f"### {result.case_id}")
            for note in result.source_policy_notes:
                lines.append(f"- {note}")
    if not any_policy:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Recommendations",
            "",
            "- Keep these fixtures as governance regression tests before adding LLM claim extraction.",
            "- Add branch-specific fixtures once Branch Bible or branch-state evidence is normalized.",
            "- Add separate behavior, voice, tone, and scene-function benchmarks later instead of mixing them into this governance baseline.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(results: Iterable[BenchmarkResult], report_path: Path = DEFAULT_REPORT_PATH) -> Path:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(results), encoding="utf-8")
    return report_path
