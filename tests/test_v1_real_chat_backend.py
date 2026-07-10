from src.v1.chat.response_models import TaskPlan
from src.v1.tasks.canon_qa import run_canon_qa
from src.v1.tasks.continuity_check import run_continuity_check_task
from src.v1.tasks.story_brief import run_story_brief
from src.v1.tasks.art_prompt import run_art_prompt


def _plan(task_type: str, provider: str = "deepseek") -> TaskPlan:
    return TaskPlan(
        task_type=task_type,
        user_intent="test",
        provider=provider,
        confidence=0.9,
    )


def _context(canon=True):
    return (
        {
            "canon_context": (
                [
                    {
                        "source_file": "canon.md",
                        "status": "canon",
                        "section_title": "Rin",
                        "excerpt": "Rin is Nexus-7.",
                    }
                ]
                if canon
                else []
            ),
            "draft_reference": [{"source_file": "draft.md", "status": "draft"}],
            "deprecated_warnings": [{"source_file": "old.md", "status": "deprecated"}],
            "missing_evidence": [] if canon else ["No canon source retrieved."],
        },
        [],
    )


def _payload(answer="### Mocked LLM Output"):
    return {
        "answer_markdown": answer,
        "risks_or_limitations": ["mock risk"],
        "suggested_next_step": "mock next step",
        "raw_payload": {"mocked": True},
    }


def test_deepseek_canon_qa_missing_key_falls_back_safely(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.build_retrieval_context",
        lambda _query: _context(canon=True),
    )

    response = run_canon_qa("Rin是什么身份？", _plan("canon_qa"))

    assert response.provider == "fake"
    assert response.metadata["fallback_reason"]


def test_deepseek_canon_qa_can_use_mocked_generation(monkeypatch):
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.build_retrieval_context",
        lambda _query: _context(canon=True),
    )
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.call_deepseek_markdown",
        lambda *args, **kwargs: _payload("### Canon Answer\nRin evidence cited."),
    )

    response = run_canon_qa("Rin是什么身份？", _plan("canon_qa"))

    assert response.provider == "deepseek"
    assert "Canon Answer" in response.answer_markdown


def test_canon_qa_without_evidence_returns_missing_evidence(monkeypatch):
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.build_retrieval_context",
        lambda _query: _context(canon=False),
    )

    response = run_canon_qa("Unknown?", _plan("canon_qa"))

    assert "NEEDS_REVIEW" in response.answer_markdown
    assert "No reliable Canon evidence" in "\n".join(response.risks_or_limitations)


def test_deepseek_story_and_art_can_use_mocked_generation(monkeypatch):
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.build_retrieval_context",
        lambda _query: _context(canon=True),
    )
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.call_deepseek_markdown",
        lambda *args, **kwargs: _payload("### Generated Brief"),
    )

    story = run_story_brief("帮我续写Mombasa安全屋下一场戏", _plan("story_brief"))
    art = run_art_prompt("生成Branch B互相包扎CG prompt", _plan("art_prompt"))

    assert story.provider == "deepseek"
    assert art.provider == "deepseek"
    assert "Generated Brief" in story.answer_markdown
    assert "Generated Brief" in art.answer_markdown


def test_continuity_check_blocks_non_canon_current_truth(monkeypatch):
    monkeypatch.setattr(
        "src.v1.tasks.llm_backend.build_retrieval_context",
        lambda _query: _context(canon=True),
    )

    deprecated = run_continuity_check_task(
        "使用Deprecated资料作为当前事实。",
        _plan("continuity_check"),
    )
    draft = run_continuity_check_task(
        "草稿可以覆盖当前Canon。",
        _plan("continuity_check"),
    )
    inspiration = run_continuity_check_task(
        "灵感碎片可以作为当前剧情事实。",
        _plan("continuity_check"),
    )

    assert "FAIL" in deprecated.answer_markdown
    assert "FAIL" in draft.answer_markdown
    assert "FAIL" in inspiration.answer_markdown
