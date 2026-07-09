"""Validate STUPID narrative state rules against a Narrative Context Pack."""

from typing import Dict, List, Optional, Set, Tuple


SUPPORTED_VALIDATION_TYPES = {"exclusive_value", "known_conflict"}


def _contains_all(text: str, keywords: List[str]) -> bool:
    lowered = text.lower()
    return all(keyword.lower() in lowered for keyword in keywords)


def _contains_any(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _find_value(text: str, values: List[str]) -> Optional[str]:
    lowered = text.lower()
    for value in values:
        if value and value.lower() in lowered:
            return value
    return None


def _citation_text(citation: Dict) -> str:
    return " ".join(
        [
            citation.get("source_file", ""),
            citation.get("status", ""),
            citation.get("summary", ""),
            citation.get("excerpt", ""),
            citation.get("reason_used", ""),
        ]
    )


def _scope(rule: Dict) -> Tuple[str, str]:
    scope = rule.get("scope", {})
    if isinstance(scope, str):
        return ("global", "global") if scope == "global" else ("branch", scope)
    return scope.get("type", "global"), scope.get("value", "global")


def _branch_markers(rule: Dict) -> List[str]:
    scope_type, scope_value = _scope(rule)
    if scope_type != "branch":
        return []
    markers = [scope_value]
    markers.extend(rule.get("evidence_keywords", {}).get("scope_any", []))
    return [marker for marker in markers if marker]


def _branch_rules(rules: List[Dict]) -> List[Dict]:
    return [rule for rule in rules if _scope(rule)[0] == "branch"]


def _branches_in_text(text: str, rules: List[Dict]) -> Set[str]:
    matches = set()
    lowered = text.lower()
    for rule in _branch_rules(rules):
        scope_value = _scope(rule)[1]
        if any(marker.lower() in lowered for marker in _branch_markers(rule)):
            matches.add(scope_value)
    return matches


def _resolve_branch(context_pack: Dict, rules: List[Dict]) -> Tuple[Optional[str], bool]:
    task = context_pack.get("task_context", {}).get("task", "")
    task_branches = _branches_in_text(task, rules)
    if len(task_branches) == 1:
        return next(iter(task_branches)), False
    if len(task_branches) > 1:
        return None, True

    evidence_branches = set()
    for citation in context_pack.get("canon_context", []):
        evidence_branches.update(_branches_in_text(_citation_text(citation), rules))
    if len(evidence_branches) == 1:
        return next(iter(evidence_branches)), False
    if len(evidence_branches) > 1:
        return None, True
    return None, False


def _task_claim_matches(task: str, rule: Dict) -> bool:
    entity = rule.get("entity", "")
    keywords = rule.get("evidence_keywords", {})
    required = [entity] if entity else []
    required.extend(keywords.get("task_all", []))
    return _contains_all(task, required) and _contains_any(
        task, keywords.get("task_any", [])
    )


def _citation_scope_allowed(
    citation: Dict, selected_branch: Optional[str], rules: List[Dict]
) -> bool:
    citation_branches = _branches_in_text(_citation_text(citation), rules)
    if not citation_branches:
        return True
    return selected_branch is not None and citation_branches == {selected_branch}


def _canon_matches(
    citation: Dict,
    rule: Dict,
    selected_branch: Optional[str],
    rules: List[Dict],
) -> bool:
    if not _citation_scope_allowed(citation, selected_branch, rules):
        return False
    text = _citation_text(citation)
    keywords = rule.get("evidence_keywords", {})
    required = [rule.get("entity", ""), rule.get("canon_value", "")]
    required.extend(keywords.get("canon_all", []))
    required = [keyword for keyword in required if keyword]
    return _contains_all(text, required) and _contains_any(
        text, keywords.get("canon_any", [])
    )


def _result(
    rule: Dict,
    validation_result: str,
    task_value: str,
    canon_evidence: List[Dict],
    context_pack: Dict,
    reason: str = "",
) -> Dict:
    scope_type, scope_value = _scope(rule)
    return {
        "rule_id": rule.get("id", ""),
        "state_type": rule.get("state_type", "character_state"),
        "validation_type": rule.get("validation_type", "known_conflict"),
        "validation_result": validation_result,
        "reason": reason,
        "scope": {"type": scope_type, "value": scope_value},
        "risk_level": rule.get("risk_level", "中"),
        "entity": rule.get("entity", ""),
        "attribute": rule.get("attribute", ""),
        "task_value": task_value,
        "canon_value": rule.get("canon_value", ""),
        "evidence_keywords": rule.get("evidence_keywords", {}),
        "resolution": rule.get("resolution", {}),
        "canon_evidence": canon_evidence,
        "deprecated_evidence": list(context_pack.get("deprecated_warnings", [])),
    }


def _evaluate_rules(context_pack: Dict, rules: List[Dict]) -> List[Dict]:
    task = context_pack.get("task_context", {}).get("task", "")
    selected_branch, branch_ambiguous = _resolve_branch(context_pack, rules)
    results = []

    for rule in rules:
        validation_type = rule.get("validation_type", "known_conflict")
        if validation_type not in SUPPORTED_VALIDATION_TYPES:
            continue
        if not _task_claim_matches(task, rule):
            continue

        scope_type, scope_value = _scope(rule)
        if scope_type == "branch" and scope_value != selected_branch:
            if selected_branch is not None:
                continue
            reason = "ambiguous_branch" if branch_ambiguous else "missing_branch_scope"
            results.append(_result(rule, "insufficient_evidence", "", [], context_pack, reason))
            continue

        canon_value = rule.get("canon_value", "")
        known_conflicts = rule.get("known_conflict_values", [])
        task_value = _find_value(task, [canon_value] + known_conflicts)
        canon_matches = [
            citation
            for citation in context_pack.get("canon_context", [])
            if _canon_matches(citation, rule, selected_branch, rules)
        ]

        if not task_value:
            results.append(
                _result(rule, "insufficient_evidence", "", canon_matches, context_pack, "unknown_value")
            )
        elif not canon_matches:
            results.append(
                _result(rule, "insufficient_evidence", task_value, [], context_pack, "missing_canon")
            )
        elif task_value == canon_value:
            results.append(_result(rule, "pass", task_value, canon_matches, context_pack))
        else:
            results.append(_result(rule, "conflict", task_value, canon_matches, context_pack))

    return results


def evaluate_continuity_rules(context_pack: Dict, rules: List[Dict]) -> List[Dict]:
    """Return structured conflict objects for confirmed Canon conflicts."""
    return [
        result
        for result in _evaluate_rules(context_pack, rules)
        if result.get("validation_result") == "conflict"
    ]


def find_rule_evidence_gaps(context_pack: Dict, rules: List[Dict]) -> List[Dict]:
    """Return state claims that cannot be resolved from applicable Canon evidence."""
    return [
        result
        for result in _evaluate_rules(context_pack, rules)
        if result.get("validation_result") == "insufficient_evidence"
    ]
