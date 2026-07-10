"""Unified v1 Daily Narrative Assistant API."""

from pathlib import Path

from src.v1.chat.request_planner import plan_request
from src.v1.chat.response_models import DailyAssistantResponse
from src.v1.chat.task_router import route_task
from src.v1.kb.lite_index import load_lite_index
from src.v1.kb.lite_retriever import retrieve_lite_evidence


def run_daily_assistant(
    user_request: str,
    provider: str = "fake",
    mode: str = "auto",
    kb_path: str | None = None,
) -> DailyAssistantResponse:
    plan = plan_request(user_request, provider=provider, mode=mode)
    if kb_path:
        plan.metadata["kb_path"] = kb_path
        path = Path(kb_path)
        if path.exists():
            kb = load_lite_index(path)
            evidence = retrieve_lite_evidence(user_request, kb, top_k=8)
            plan.metadata["lite_evidence"] = evidence
            plan.metadata["lite_kb_status"] = "loaded"
            plan.metadata["lite_kb_source_count"] = kb.source_count
        else:
            plan.metadata["lite_evidence"] = []
            plan.metadata["lite_kb_status"] = "missing"
            plan.metadata["lite_kb_warning"] = f"Lite KB not found: {kb_path}"
    return route_task(user_request, plan)
