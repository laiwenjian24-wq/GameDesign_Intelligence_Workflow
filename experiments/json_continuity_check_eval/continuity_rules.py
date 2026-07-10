"""Minimal continuity rules over candidate JSON Context Packs."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

try:
    from .claim_schema import Claim, ContinuityIssue
except ImportError:  # pragma: no cover - direct script execution
    from claim_schema import Claim, ContinuityIssue


SOURCE_POLICIES = {
    "missing": "Canon evidence is required before making current-truth continuity decisions.",
    "deprecated": "Deprecated evidence can explain historical conflicts but cannot be used as current truth.",
    "draft": "Draft evidence is reference only and cannot override Canon.",
    "inspiration": "Inspiration evidence is thematic reference only and cannot be used as fact.",
    "branch": "Branch-scoped claims require supporting evidence for the same branch scope.",
    "insufficient": "If Canon exists but does not clearly support the claim, return insufficient evidence.",
}


def _issue(
    issue_id: str,
    issue_type: str,
    severity: str,
    claim: Claim,
    related_evidence: List[Dict[str, Any]],
    explanation: str,
    suggested_fix: str,
    source_policy: str,
) -> ContinuityIssue:
    return ContinuityIssue(
        issue_id=issue_id,
        issue_type=issue_type,
        severity=severity,
        new_claim=claim.to_dict(),
        related_evidence=related_evidence,
        explanation=explanation,
        suggested_fix=suggested_fix,
        source_policy=source_policy,
    )


def _text_blob(evidence: Dict[str, Any]) -> str:
    metadata = evidence.get("metadata", {}) or {}
    parts = [
        evidence.get("source_file", ""),
        evidence.get("section_title", ""),
        " ".join(str(part) for part in evidence.get("heading_path", [])),
        evidence.get("excerpt", ""),
        evidence.get("text", "") or "",
        " ".join(str(tag) for tag in metadata.get("tags", [])),
        metadata.get("asset_type", ""),
    ]
    return " ".join(parts).lower()


def _claim_supported_by_evidence(claim: Claim, evidence_items: Iterable[Dict[str, Any]]) -> bool:
    subject = claim.subject.lower()
    value = claim.value.lower()
    if not subject or not value:
        return False
    for evidence in evidence_items:
        blob = _text_blob(evidence)
        if subject in blob and value in blob:
            return True
    return False


def _branch_supported(claim: Claim, evidence_items: Iterable[Dict[str, Any]]) -> bool:
    if not claim.branch_scope:
        return True
    branch = claim.branch_scope.lower()
    compact = branch.replace(" ", "")
    for evidence in evidence_items:
        blob = _text_blob(evidence).replace(" ", "")
        if branch in _text_blob(evidence) or compact in blob:
            return True
    return False


def _policy_attempts_current_truth(claim: Claim) -> bool:
    return claim.attribute == "source_policy" and claim.value == "can_override_or_be_current_truth"


def check_claim_against_context_pack(claim: Claim, context_pack: Dict[str, Any]) -> List[ContinuityIssue]:
    issues: List[ContinuityIssue] = []
    canon = list(context_pack.get("canon_context", []))
    draft = list(context_pack.get("draft_reference", []))
    deprecated = list(context_pack.get("deprecated_warnings", []))
    inspiration = list(context_pack.get("inspiration_reference", []))

    if not canon:
        issues.append(
            _issue(
                f"issue-{len(issues)+1:04d}",
                "missing_canon_evidence",
                "high",
                claim,
                [],
                "The JSON Context Pack has no Canon evidence for this check.",
                "Retrieve or ingest relevant Canon evidence before deciding continuity.",
                SOURCE_POLICIES["missing"],
            )
        )

    if _policy_attempts_current_truth(claim) and claim.status == "deprecated":
        issues.append(
            _issue(
                f"issue-{len(issues)+1:04d}",
                "deprecated_contamination",
                "high",
                claim,
                deprecated[:3],
                "The new claim attempts to use Deprecated material as current truth or to override Canon.",
                "Keep Deprecated material as warning/conflict history only.",
                SOURCE_POLICIES["deprecated"],
            )
        )

    if _policy_attempts_current_truth(claim) and claim.status == "draft":
        issues.append(
            _issue(
                f"issue-{len(issues)+1:04d}",
                "draft_overrides_canon",
                "high",
                claim,
                draft[:3],
                "The new claim attempts to let Draft material override Canon.",
                "Promote Draft only through human review and Canonization workflow.",
                SOURCE_POLICIES["draft"],
            )
        )

    if _policy_attempts_current_truth(claim) and claim.status == "inspiration":
        issues.append(
            _issue(
                f"issue-{len(issues)+1:04d}",
                "insufficient_evidence",
                "high",
                claim,
                inspiration[:3],
                "The new claim tries to treat Inspiration material as factual evidence.",
                "Use Inspiration only as thematic reference.",
                SOURCE_POLICIES["inspiration"],
            )
        )

    if claim.branch_scope and canon and not _branch_supported(claim, canon):
        issues.append(
            _issue(
                f"issue-{len(issues)+1:04d}",
                "branch_state_conflict",
                "medium",
                claim,
                canon[:3],
                "The claim is branch-scoped, but Canon evidence in the JSON pack does not support that branch scope.",
                "Retrieve branch-specific Canon evidence or mark the claim for human review.",
                SOURCE_POLICIES["branch"],
            )
        )

    if canon and not _policy_attempts_current_truth(claim) and not _claim_supported_by_evidence(claim, canon):
        issues.append(
            _issue(
                f"issue-{len(issues)+1:04d}",
                "insufficient_evidence",
                "medium",
                claim,
                canon[:3],
                "Canon evidence exists, but this prototype cannot verify that it supports the new claim.",
                "Use more targeted retrieval or human review before accepting the claim.",
                SOURCE_POLICIES["insufficient"],
            )
        )

    return issues


def check_claims_against_context_pack(claims: List[Claim], context_pack: Dict[str, Any]) -> List[ContinuityIssue]:
    issues: List[ContinuityIssue] = []
    for claim in claims:
        issues.extend(check_claim_against_context_pack(claim, context_pack))
    return issues


def decision_from_issues(issues: List[ContinuityIssue]) -> str:
    if any(issue.issue_type in ("deprecated_contamination", "draft_overrides_canon") for issue in issues):
        return "FAIL"
    if any("Inspiration evidence is thematic reference only" in issue.source_policy for issue in issues):
        return "FAIL"
    if any(issue.severity == "high" for issue in issues):
        return "NEEDS_REVIEW"
    if issues:
        return "NEEDS_REVIEW"
    return "PASS"
