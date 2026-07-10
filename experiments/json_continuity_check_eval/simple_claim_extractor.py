"""Deterministic prototype claim extractor.

This is intentionally shallow. It identifies simple continuity-relevant claims
without calling an LLM or encoding final story conclusions.
"""

from __future__ import annotations

import re
from typing import List

try:
    from .claim_schema import Claim
except ImportError:  # pragma: no cover - direct script execution
    from claim_schema import Claim


BRANCH_PATTERN = re.compile(r"Branch\s*([ABC])|分支\s*([ABC])", re.IGNORECASE)
IS_PATTERN = re.compile(r"(?P<subject>[A-Za-z0-9_\-\u4e00-\u9fff]+?)\s*(?:是|为)\s*(?P<value>[^。；;，,\n]+)")
NOT_PATTERN = re.compile(r"(?P<subject>[A-Za-z0-9_\-\u4e00-\u9fff]+?)\s*不是\s*(?P<value>[^。；;，,\n]+)")
INJURY_PATTERN = re.compile(r"(?P<subject>[A-Za-z0-9_\-\u4e00-\u9fff]+?)\s*(?P<side>左腿|右腿|左肩|右肩|left leg|right leg)\s*(?:受伤|负伤|擦伤|injured)", re.IGNORECASE)


def _branch_scope(text: str) -> str | None:
    match = BRANCH_PATTERN.search(text)
    if not match:
        return None
    return f"Branch {match.group(1) or match.group(2)}".upper().replace("BRANCH", "Branch")


def _status_intent(text: str) -> str | None:
    lower = text.lower()
    if any(term in text for term in ("废弃", "旧版", "Deprecated")) or "deprecated" in lower:
        return "deprecated"
    if any(term in text for term in ("草稿", "Draft")) or "draft" in lower:
        return "draft"
    if any(term in text for term in ("灵感", "Inspiration")) or "inspiration" in lower:
        return "inspiration"
    return None


def extract_claims(text: str) -> List[Claim]:
    claims: List[Claim] = []
    branch_scope = _branch_scope(text)
    status_intent = _status_intent(text)

    if any(term in text for term in ("覆盖Canon", "覆盖 Canon", "覆盖当前Canon", "作为当前事实", "当前剧情事实", "current fact")):
        claims.append(
            Claim(
                claim_id=f"claim-{len(claims)+1:04d}",
                raw_text=text,
                subject=status_intent or "source_material",
                attribute="source_policy",
                value="can_override_or_be_current_truth",
                branch_scope=branch_scope,
                status=status_intent,
                confidence=0.85,
                extraction_method="deterministic_policy_pattern",
                metadata={"policy_intent": True},
            )
        )

    for match in INJURY_PATTERN.finditer(text):
        claims.append(
            Claim(
                claim_id=f"claim-{len(claims)+1:04d}",
                raw_text=text,
                subject=match.group("subject"),
                attribute="injury",
                value=match.group("side"),
                branch_scope=branch_scope,
                status=status_intent,
                confidence=0.75,
                extraction_method="deterministic_injury_pattern",
            )
        )

    for match in NOT_PATTERN.finditer(text):
        claims.append(
            Claim(
                claim_id=f"claim-{len(claims)+1:04d}",
                raw_text=text,
                subject=match.group("subject"),
                attribute="not_identity",
                value=match.group("value").strip(),
                branch_scope=branch_scope,
                status=status_intent,
                confidence=0.7,
                extraction_method="deterministic_not_pattern",
            )
        )

    for match in IS_PATTERN.finditer(text):
        claims.append(
            Claim(
                claim_id=f"claim-{len(claims)+1:04d}",
                raw_text=text,
                subject=match.group("subject"),
                attribute="identity",
                value=match.group("value").strip(),
                branch_scope=branch_scope,
                status=status_intent,
                confidence=0.7,
                extraction_method="deterministic_is_pattern",
            )
        )

    if not claims:
        claims.append(
            Claim(
                claim_id="claim-0001",
                raw_text=text,
                subject="unknown",
                attribute="unknown",
                value=text,
                branch_scope=branch_scope,
                status=status_intent,
                confidence=0.25,
                extraction_method="fallback_raw_text",
            )
        )
    return claims
