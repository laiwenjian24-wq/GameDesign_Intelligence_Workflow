from src.v1.chat.request_planner import plan_request


def test_planner_detects_canon_qa():
    plan = plan_request("Rin是什么身份？")
    assert plan.task_type == "canon_qa"
    assert "Rin" in plan.entities


def test_planner_detects_continuity_check():
    plan = plan_request("Branch B中Rin右腿受伤，这样能用吗？")
    assert plan.task_type == "continuity_check"
    assert plan.branch_scope == "Branch B"


def test_planner_detects_story_brief():
    plan = plan_request("帮我续写Mombasa安全屋下一场戏")
    assert plan.task_type == "story_brief"


def test_planner_detects_art_prompt():
    plan = plan_request("生成Branch B互相包扎CG prompt")
    assert plan.task_type == "art_prompt"


def test_planner_unknown_request_has_low_confidence():
    plan = plan_request("随便看看")
    assert plan.task_type == "unknown"
    assert plan.confidence < 0.5


def test_deepseek_missing_key_falls_back_without_api(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    plan = plan_request("Rin是什么身份？", provider="deepseek")
    assert plan.provider == "fake"
    assert plan.task_type == "canon_qa"
    assert plan.fallback_reason
