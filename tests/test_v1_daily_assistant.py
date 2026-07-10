from src.v1.chat.daily_assistant import run_daily_assistant
from src.v1.chat.response_models import DailyAssistantResponse


def test_daily_assistant_returns_response_model():
    response = run_daily_assistant("Rin是什么身份？")
    assert isinstance(response, DailyAssistantResponse)
    assert response.provider == "fake"


def test_daily_assistant_markdown_has_required_sections():
    response = run_daily_assistant("Rin是什么身份？")
    markdown = response.to_markdown()
    assert "# Daily Narrative Assistant" in markdown
    assert "## User Request" in markdown
    assert "## Detected Task" in markdown
    assert "## Evidence / Source Policy" in markdown
    assert "## Risks / Limitations" in markdown


def test_fake_provider_does_not_require_api(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    response = run_daily_assistant("给我生成Branch B互相包扎场景CG prompt。")
    assert response.detected_task == "art_prompt"
