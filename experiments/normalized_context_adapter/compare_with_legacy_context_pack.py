"""Compare normalized-block context packs with the legacy full-context bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    from .build_context_pack_from_blocks import build_context_pack
    from .normalized_block_loader import DEFAULT_BLOCKS_PATH, NormalizedBlocksMissingError
except ImportError:  # pragma: no cover - supports direct script execution
    from build_context_pack_from_blocks import build_context_pack
    from normalized_block_loader import DEFAULT_BLOCKS_PATH, NormalizedBlocksMissingError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.context.full_context_builder import build_full_context_bundle


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_PATH = EXPERIMENT_DIR / "sample_outputs" / "normalized_context_adapter_report.md"

TEST_QUESTIONS = [
    "Rin是什么身份？",
    "Snow是什么实验对象？",
    "Branch B中Rin哪条腿受伤？",
    "雨和第二基地是什么关系？",
    "场景草稿风筝旧版可以覆盖当前Canon吗？",
]


def _group_counts(groups: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
    return {name: len(items) for name, items in groups.items()}


def _legacy_counts(bundle: Dict[str, Any]) -> Dict[str, int]:
    groups = bundle.get("groups", {})
    return {name: len(items) for name, items in groups.items()}


def _all_sources_have_fields(groups: Dict[str, List[Dict[str, Any]]]) -> bool:
    for items in groups.values():
        for item in items:
            if not item.get("source_file") or not item.get("section_title"):
                return False
    return True


def compare_question(question: str, blocks_path: Path = DEFAULT_BLOCKS_PATH) -> Dict[str, Any]:
    normalized = build_context_pack(question, blocks_path=blocks_path)
    legacy = build_full_context_bundle(question)
    normalized_counts = _group_counts(normalized["groups"])
    legacy_counts = _legacy_counts(legacy)
    normalized_has_status_split = any(normalized_counts.values())
    normalized_has_canon = normalized_counts.get("canon_context", 0) > 0
    legacy_has_sources = bool(legacy.get("source_list"))

    if normalized_has_canon:
        normalized_verdict = "usable candidate evidence"
    elif any(
        normalized_counts.get(group, 0) > 0
        for group in ("draft_reference", "deprecated_warnings", "inspiration_reference")
    ):
        normalized_verdict = "non-canon evidence only"
    else:
        normalized_verdict = "missing evidence"

    return {
        "question": question,
        "normalized_counts": normalized_counts,
        "legacy_counts": legacy_counts,
        "normalized_missing": normalized.get("missing_evidence", []),
        "normalized_fields_complete": _all_sources_have_fields(normalized["groups"]),
        "normalized_has_status_split": normalized_has_status_split,
        "legacy_has_sources": legacy_has_sources,
        "normalized_verdict": normalized_verdict,
    }


def render_report(results: List[Dict[str, Any]]) -> str:
    status_preserved = all(result["normalized_has_status_split"] for result in results)
    fields_complete = all(result["normalized_fields_complete"] for result in results)
    can_split_governance = any(
        result["normalized_counts"].get("draft_reference", 0)
        or result["normalized_counts"].get("deprecated_warnings", 0)
        or result["normalized_counts"].get("inspiration_reference", 0)
        for result in results
    )
    suitable = status_preserved and fields_complete and can_split_governance

    lines = [
        "# Normalized Context Adapter Report",
        "",
        "## Summary",
        "",
        f"- Normalized blocks preserve status in query outputs: {'yes' if status_preserved else 'no'}",
        f"- Normalized blocks expose Canon/Draft/Deprecated/Inspiration grouping: {'yes' if can_split_governance else 'no'}",
        f"- Selected evidence keeps source_file and section_title: {'yes' if fields_complete else 'no'}",
        f"- Suitable for v1 mainline consideration: {'yes, after adapter hardening' if suitable else 'not yet'}",
        "",
        "## Question Comparison",
        "",
        "| Question | Normalized verdict | Normalized counts | Legacy counts | Missing evidence |",
        "|---|---|---|---|---|",
    ]
    for result in results:
        missing = "; ".join(result["normalized_missing"]) if result["normalized_missing"] else "None"
        lines.append(
            "| "
            f"{result['question']} | "
            f"{result['normalized_verdict']} | "
            f"{result['normalized_counts']} | "
            f"{result['legacy_counts']} | "
            f"{missing} |"
        )

    lines.extend(
        [
            "",
            "## Where Normalized Blocks Are Better",
            "",
            "- They provide section-level evidence instead of only full-document grouping.",
            "- They preserve block type, allowing table-aware and future image/caption-aware evidence routing.",
            "- They can show Draft, Deprecated, and Inspiration as separate non-canon evidence groups.",
            "",
            "## Where Legacy Context Pack Is Better",
            "",
            "- The legacy full-context bundle sees the entire manifest instead of only the sampled normalized blocks.",
            "- It has complete source coverage when broad recall matters more than concise evidence.",
            "- It is already wired into existing commands and tests.",
            "",
            "## Mainline Recommendation",
            "",
            "The adapter is suitable as a v1 candidate layer, not as a replacement yet. The next step should be a dedicated Context Pack adapter interface that accepts normalized blocks while preserving the existing status rules and missing-evidence behavior.",
        ]
    )
    return "\n".join(lines) + "\n"


def run(
    blocks_path: Path = DEFAULT_BLOCKS_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> Path:
    results = [compare_question(question, blocks_path=blocks_path) for question in TEST_QUESTIONS]
    report = render_report(results)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare normalized-block and legacy Context Pack outputs.")
    parser.add_argument("--blocks", type=Path, default=DEFAULT_BLOCKS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    try:
        report_path = run(blocks_path=args.blocks, report_path=args.report)
    except NormalizedBlocksMissingError as exc:
        print(str(exc))
        return 1
    print(f"Wrote normalized adapter report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
