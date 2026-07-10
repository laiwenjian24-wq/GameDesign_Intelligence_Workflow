from src.v1.chat.request_planner import plan_request
from src.v1.chat.task_router import route_task


def _route(text):
    plan = plan_request(text)
    return route_task(text, plan)


def test_router_routes_canon_qa():
    response = _route("Rin是什么身份？")
    assert response.detected_task == "canon_qa"


def test_router_routes_continuity_check():
    response = _route("Branch B中Rin右腿受伤，这样能用吗？")
    assert response.detected_task == "continuity_check"


def test_router_routes_story_brief():
    response = _route("帮我续写Mombasa安全屋下一场戏")
    assert response.detected_task == "story_brief"


def test_router_routes_art_prompt():
    response = _route("生成Branch B互相包扎CG prompt")
    assert response.detected_task == "art_prompt"


def test_router_unknown_has_fallback_response():
    response = _route("随便看看")
    assert response.detected_task == "unknown"
    assert "不能可靠判断" in response.answer_markdown
