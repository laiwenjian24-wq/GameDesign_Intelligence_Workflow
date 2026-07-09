"""Continuity checker based on Narrative Context Pack.

This module does not call an LLM, does not use embeddings, and does not depend
on loose retrieval results directly. The flow is:

query -> retrieval -> context_builder -> Context Pack -> continuity report
"""

from pathlib import Path
from typing import Dict, List, Optional

from src.context.context_builder import build_context_pack
from src.rules.continuity_rule_evaluator import (
    evaluate_continuity_rules,
    find_rule_evidence_gaps,
)
from src.rules.continuity_rule_loader import load_continuity_rules


HIGH = "高"
MEDIUM = "中"
LOW = "低"


def _conflict_text(conflict: Dict) -> str:
    """Build report text from a structured conflict object."""
    entity = conflict.get("entity", "该对象")
    attribute = conflict.get("attribute", "设定")
    task_value = conflict.get("task_value", "输入值")
    canon_value = conflict.get("canon_value", "Canon 值")
    return (
        f"输入使用 {entity} 的 {attribute} = {task_value}，"
        f"但 Context Pack 中 Canon 指向 {attribute} = {canon_value}。"
    )


def _canon_interpretation(conflict: Dict) -> str:
    """Build the Canon interpretation for report output."""
    entity = conflict.get("entity", "该对象")
    attribute = conflict.get("attribute", "设定")
    canon_value = conflict.get("canon_value", "Canon 值")
    return f"Final Decision 应采用 canon：{entity} 的 {attribute} = {canon_value}。"


def _deprecated_interpretation(conflict: Dict) -> str:
    """Explain how Deprecated evidence is used for report output."""
    deprecated_evidence = conflict.get("deprecated_evidence", [])
    policy = conflict.get("resolution", {}).get("deprecated_policy", "explain_only")
    if deprecated_evidence and policy == "explain_only":
        return "Deprecated Evidence 仅作为旧版本 / 冲突来源解释，不能覆盖 Canon。"
    return "未召回对应 Deprecated Evidence；但 Task claim 已与 Canon Evidence 冲突，因此仍判定为高风险。"


def _rewrite_from_conflict(conflict: Dict) -> str:
    """Build a generic rewrite suggestion from structured conflict metadata."""
    entity = conflict.get("entity", "该对象")
    attribute = conflict.get("attribute", "设定")
    task_value = conflict.get("task_value", "输入值")
    canon_value = conflict.get("canon_value", "Canon 值")
    return f"将 {entity} 的 {attribute} 从 {task_value} 改为 {canon_value}。"


def _final_decision_from_conflict(conflict: Dict) -> str:
    """Build a generic final decision from structured conflict metadata."""
    entity = conflict.get("entity", "该对象")
    attribute = conflict.get("attribute", "设定")
    canon_value = conflict.get("canon_value", "Canon 值")
    task_value = conflict.get("task_value", "输入值")
    return (
        f"采用 canon：{entity} 的 {attribute} = {canon_value}。"
        f"当前输入不可直接通过，应修改 {task_value} 为 {canon_value}。"
    )


def _format_conflict(raw_conflict: Dict) -> Dict:
    """Add report-facing text fields without changing rule matching output."""
    conflict = dict(raw_conflict)
    conflict["conflict"] = _conflict_text(conflict)
    conflict["canon_interpretation"] = _canon_interpretation(conflict)
    conflict["deprecated_interpretation"] = _deprecated_interpretation(conflict)
    conflict["rewrite_suggestion"] = _rewrite_from_conflict(conflict)
    return conflict


def _build_conflict_analysis(
    context_pack: Dict, rule_path: Optional[Path] = None
) -> List[Dict]:
    """Run rule-based conflict checks over a Context Pack."""
    rules = load_continuity_rules(rule_path)
    return [
        _format_conflict(conflict)
        for conflict in evaluate_continuity_rules(context_pack, rules)
    ]


def _build_missing_evidence(
    context_pack: Dict, conflicts: List[Dict], rules: List[Dict]
) -> List[str]:
    """Combine Context Pack missing evidence with check-specific gaps."""
    missing = list(context_pack.get("missing_evidence", []))

    for gap in find_rule_evidence_gaps(context_pack, rules):
        entity = gap.get("entity", "该对象")
        attribute = gap.get("attribute", "设定")
        task_value = gap.get("task_value") or "未识别值"
        missing.append(
            f"任务涉及 {entity} 的 {attribute} = {task_value}，"
            "但 Context Pack 中缺少对应 Canon Evidence，需要人工确认。"
        )
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
        return _final_decision_from_conflict(conflicts[0])
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


def run_continuity_check(
    input_text: str,
    index_dir: Path,
    top_k: int = 5,
    rule_path: Optional[Path] = None,
) -> Dict:
    """Build Context Pack first, then run continuity checks from it."""
    context_pack = build_context_pack(input_text, index_dir, top_k=top_k)
    rules = load_continuity_rules(rule_path)
    conflicts = [
        _format_conflict(conflict)
        for conflict in evaluate_continuity_rules(context_pack, rules)
    ]
    missing_evidence = _build_missing_evidence(context_pack, conflicts, rules)
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
