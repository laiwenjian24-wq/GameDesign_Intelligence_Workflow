"""Unified v1 Daily Narrative Assistant API."""

from src.v1.chat.request_planner import plan_request
from src.v1.chat.response_models import DailyAssistantResponse
from src.v1.chat.task_router import route_task


def run_daily_assistant(
    user_request: str,
    provider: str = "fake",
    mode: str = "auto",
) -> DailyAssistantResponse:
    plan = plan_request(user_request, provider=provider, mode=mode)
    return route_task(user_request, plan)
