"""Source policy text for v1 continuity workflows."""


CANON_POLICY = "Canon is current truth."
DRAFT_POLICY = "Draft is reference only."
DEPRECATED_POLICY = "Deprecated is historical/conflict evidence only."
INSPIRATION_POLICY = "Inspiration is not fact."
UNKNOWN_POLICY = "Unknown requires human review."
NO_AUTO_CANON_POLICY = "LLM cannot automatically canonize new material."

SOURCE_POLICIES = {
    "canon": CANON_POLICY,
    "draft": DRAFT_POLICY,
    "deprecated": DEPRECATED_POLICY,
    "inspiration": INSPIRATION_POLICY,
    "unknown": UNKNOWN_POLICY,
    "no_auto_canon": NO_AUTO_CANON_POLICY,
}


def get_source_policy(status: str) -> str:
    return SOURCE_POLICIES.get(str(status or "unknown").lower(), UNKNOWN_POLICY)
