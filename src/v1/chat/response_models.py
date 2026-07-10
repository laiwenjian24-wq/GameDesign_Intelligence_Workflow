"""Response models for the v1 Daily Narrative Assistant."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskPlan:
    task_type: str
    user_intent: str
    entities: List[str] = field(default_factory=list)
    aliases: Dict[str, List[str]] = field(default_factory=dict)
    branch_scope: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    requested_output: str = "markdown"
    confidence: float = 0.0
    clarification_needed: bool = False
    clarification_question: str = ""
    provider: str = "fake"
    fallback_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DailyAssistantResponse:
    user_request: str
    detected_task: str
    answer_markdown: str
    evidence_or_source_policy: List[str]
    risks_or_limitations: List[str]
    suggested_next_step: str
    debug_task_plan: Dict[str, Any]
    provider: str = "fake"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Daily Narrative Assistant",
            "",
            "## User Request",
            "",
            self.user_request,
            "",
            "## Detected Task",
            "",
            self.detected_task,
            "",
            "## Answer / Output",
            "",
            self.answer_markdown.strip(),
            "",
            "## Evidence / Source Policy",
            "",
        ]
        lines.extend(f"- {item}" for item in self.evidence_or_source_policy)
        lines.extend(["", "## Risks / Limitations", ""])
        lines.extend(f"- {item}" for item in self.risks_or_limitations)
        lines.extend(
            [
                "",
                "## Suggested Next Step",
                "",
                self.suggested_next_step,
                "",
                "## Debug Task Plan",
                "",
                "```json",
                _json_dumps(self.debug_task_plan),
                "```",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"


def _json_dumps(payload: Dict[str, Any]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)
