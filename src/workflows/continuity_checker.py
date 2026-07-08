"""Continuity checker based on Narrative Context Pack.

This module does not call an LLM, does not use embeddings, and does not depend
on loose retrieval results directly. The flow is:

query -> retrieval -> context_builder -> Context Pack -> continuity report
"""

from pathlib import Path
from typing import Dict, List

from src.context.context_builder import build_context_pack


HIGH = "高"
MEDIUM = "中"
LOW = "低"


def _contains_all(text: str, keywords: List[str]) -> bool:
    """Return True when all keywords are present in text."""
    lowered = text.lower()
    return all(keyword.lower() in lowered for keyword in keywords)


def _citation_text(citation: Dict) -> str:
    """Return searchable text from a Context Pack citation."""
    return " ".join(
        [
            citation.get("source_file", ""),
            citation.get("status", ""),
            citation.get("summary", ""),
            citation.get("excerpt", ""),
            citation.get("reason_used", ""),
        ]
    )


def _find_rin_leg_conflict(context_pack: Dict) -> Dict:
    """Detect the known Rin right-leg claim vs canon left-leg injury conflict.

    Deprecated evidence is useful as an explanation of where the wrong version
    may have come from, but it is not required to classify a Canon conflict as
    high risk.
    """
    task = context_pack.get("task_context", {}).get("task", "")
    mentions_rin_right_leg = _contains_all(task, ["rin", "右腿"])
    mentions_care_context = any(
        keyword in task for keyword in ["受伤", "换药", "包扎", "治疗", "伤"]
    )

    if not (mentions_rin_right_leg and mentions_care_context):
        return {}

    canon_matches = []
    for citation in context_pack.get("canon_context", []):
        citation_text = _citation_text(citation)
        has_rin_left_leg = _contains_all(citation_text, ["Rin", "左腿"])
        has_injury_evidence = any(
            keyword in citation_text
            for keyword in ["受伤", "擦伤", "擦过", "伤口", "负伤"]
        )
        if has_rin_left_leg and has_injury_evidence:
            canon_matches.append(citation)

    deprecated_matches = list(context_pack.get("deprecated_warnings", []))

    if not canon_matches:
        return {}

    if deprecated_matches:
        deprecated_interpretation = "Deprecated Evidence 仅作为旧版本 / 冲突来源解释，不能覆盖 Canon。"
    else:
        deprecated_interpretation = "未召回对应 Deprecated Evidence；但 Task claim 已与 Canon Evidence 冲突，因此仍判定为高风险。"

    return {
        "risk_level": HIGH,
        "conflict": "输入使用 Rin 右腿受伤 / 换药，但 Context Pack 中 Canon 指向 Rin 左腿受伤 / 擦伤。",
        "canon_interpretation": "Final Decision 应采用 canon：Rin 左腿受伤 / 擦伤。",
        "deprecated_interpretation": deprecated_interpretation,
        "rewrite_suggestion": "Mouse 在安全屋里给 Rin 的左腿换药。",
        "canon_evidence": canon_matches,
        "deprecated_evidence": deprecated_matches,
    }


def _build_conflict_analysis(context_pack: Dict) -> List[Dict]:
    """Run rule-based conflict checks over a Context Pack."""
    conflicts = []
    rin_leg_conflict = _find_rin_leg_conflict(context_pack)
    if rin_leg_conflict:
        conflicts.append(rin_leg_conflict)
    return conflicts


def _build_missing_evidence(context_pack: Dict, conflicts: List[Dict]) -> List[str]:
    """Combine Context Pack missing evidence with check-specific gaps."""
    missing = list(context_pack.get("missing_evidence", []))

    task = context_pack.get("task_context", {}).get("task", "")
    if "Rin" in task and "受伤" in task and not context_pack.get("canon_context"):
        missing.append("任务涉及 Rin 伤势，但 Context Pack 中缺少 Canon Evidence。")

    if conflicts:
        return missing

    if _contains_all(task, ["rin", "右腿"]) and not context_pack.get(
        "deprecated_warnings"
    ):
        missing.append("任务提到 Rin 右腿，但 Context Pack 中没有检索到对应旧设定或 Canon 依据，需要人工确认。")

    return missing


def _risk_level(conflicts: List[Dict], missing_evidence: List[str]) -> str:
    """Compute final risk level."""
    if any(conflict.get("risk_level") == HIGH for conflict in conflicts):
        return HIGH
    if missing_evidence:
        return MEDIUM
    return LOW


def _final_decision(risk_level: str, conflicts: List[Dict]) -> str:
    """Build final decision from Context Pack analysis."""
    if risk_level == HIGH and conflicts:
        return "采用 canon：Rin 左腿受伤。当前输入不可直接通过，应修改右腿为左腿。"
    if risk_level == MEDIUM:
        return "证据不足，暂缓通过；需要补充 Canon Evidence 或人工确认。"
    return "未发现明确 Canon 冲突，可暂时通过，但正式入库前仍建议人工复核。"


def _rewrite_suggestion(conflicts: List[Dict]) -> str:
    """Return the most specific rewrite suggestion available."""
    for conflict in conflicts:
        suggestion = conflict.get("rewrite_suggestion")
        if suggestion:
            return suggestion
    return "暂无必须改写项。"


def run_continuity_check(input_text: str, index_dir: Path, top_k: int = 5) -> Dict:
    """Build Context Pack first, then run continuity checks from it."""
    context_pack = build_context_pack(input_text, index_dir, top_k=top_k)
    conflicts = _build_conflict_analysis(context_pack)
    missing_evidence = _build_missing_evidence(context_pack, conflicts)
    risk_level = _risk_level(conflicts, missing_evidence)

    return {
        "task": input_text,
        "risk_level": risk_level,
        "canon_evidence": context_pack.get("canon_context", []),
        "deprecated_evidence": context_pack.get("deprecated_warnings", []),
        "draft_reference": context_pack.get("draft_reference", []),
        "missing_evidence": missing_evidence,
        "conflict_analysis": conflicts,
        "final_decision": _final_decision(risk_level, conflicts),
        "rewrite_suggestion": _rewrite_suggestion(conflicts),
        "context_pack": context_pack,
    }


def _append_evidence(lines: List[str], citations: List[Dict]) -> None:
    """Append evidence citations with required fields."""
    if not citations:
        lines.append("- 无")
        return

    for citation in citations:
        lines.append(f"- source_file: {citation.get('source_file', '')}")
        lines.append(f"  - status: {citation.get('status', 'unknown')}")
        lines.append(f"  - excerpt: {citation.get('excerpt', '')}")
        lines.append(f"  - reason_used: {citation.get('reason_used', '')}")


def format_continuity_report(report: Dict) -> str:
    """Format a Context-Pack-based continuity report."""
    lines = [
        "# Continuity Report",
        "",
        "## Task",
        f"- {report.get('task', '')}",
        "",
        "## Risk Level",
        f"- {report.get('risk_level', LOW)}",
        "",
        "## Canon Evidence",
    ]

    _append_evidence(lines, report.get("canon_evidence", []))

    lines.extend(["", "## Deprecated Evidence"])
    _append_evidence(lines, report.get("deprecated_evidence", []))

    lines.extend(["", "## Draft Reference"])
    _append_evidence(lines, report.get("draft_reference", []))

    lines.extend(["", "## Missing Evidence"])
    missing = report.get("missing_evidence", [])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")

    lines.extend(["", "## Conflict Analysis"])
    conflicts = report.get("conflict_analysis", [])
    if conflicts:
        for conflict in conflicts:
            lines.append(f"- {conflict.get('conflict', '')}")
            lines.append(f"  - {conflict.get('canon_interpretation', '')}")
            lines.append(f"  - {conflict.get('deprecated_interpretation', '')}")
    else:
        lines.append("- 未发现明确 Canon 冲突。")

    lines.extend(["", "## Final Decision"])
    lines.append(f"- {report.get('final_decision', '')}")

    lines.extend(["", "## Rewrite Suggestion"])
    lines.append(f"- {report.get('rewrite_suggestion', '')}")

    return "\n".join(lines)
