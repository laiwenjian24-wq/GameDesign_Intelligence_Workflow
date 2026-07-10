"""Task router for the v1 Daily Narrative Assistant."""

from src.v1.chat.response_models import DailyAssistantResponse, TaskPlan
from src.v1.tasks.art_prompt import run_art_prompt
from src.v1.tasks.canon_qa import run_canon_qa
from src.v1.tasks.continuity_check import run_continuity_check_task
from src.v1.tasks.story_brief import run_story_brief


def route_task(user_request: str, plan: TaskPlan) -> DailyAssistantResponse:
    if plan.task_type == "canon_qa":
        return run_canon_qa(user_request, plan)
    if plan.task_type == "continuity_check":
        return run_continuity_check_task(user_request, plan)
    if plan.task_type == "story_brief":
        return run_story_brief(user_request, plan)
    if plan.task_type == "art_prompt":
        return run_art_prompt(user_request, plan)
    return DailyAssistantResponse(
        user_request=user_request,
        detected_task="unknown",
        answer_markdown=(
            "我还不能可靠判断这个请求属于设定问答、连续性检查、场景 brief，"
            "还是美术 prompt。请换一种更具体的说法。"
        ),
        evidence_or_source_policy=[
            "Canon is current truth.",
            "Draft / Deprecated / Inspiration cannot be used as current fact.",
        ],
        risks_or_limitations=["Unknown task type; no production decision should be made."],
        suggested_next_step="明确选择 Canon QA、Continuity Check、Story Brief 或 Art Prompt。",
        debug_task_plan=plan.to_dict(),
        provider=plan.provider,
    )
