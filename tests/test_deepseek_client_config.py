"""Tests for DeepSeek provider configuration."""

import pytest

import main
from src.llm.client import DeepSeekLLMClient, FakeLLMClient, LLMProviderError


def test_missing_deepseek_api_key_gives_clear_error(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(LLMProviderError) as excinfo:
        DeepSeekLLMClient()

    assert "DEEPSEEK_API_KEY is not set" in str(excinfo.value)


def test_provider_fake_remains_default(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    provider, task_args = main._extract_provider(["Rin是什么身份？"])
    client = main._llm_client_for_provider(provider)

    assert provider == "fake"
    assert task_args == ["Rin是什么身份？"]
    assert isinstance(client, FakeLLMClient)


def test_cli_can_parse_provider_deepseek():
    provider, task_args = main._extract_provider(
        ["Rin是什么身份？", "--provider", "deepseek"]
    )

    assert provider == "deepseek"
    assert task_args == ["Rin是什么身份？"]


def test_cli_deepseek_missing_key_has_no_traceback(monkeypatch, capsys):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(main, "build_llamaindex_nodes", lambda **kwargs: None)

    exit_code = main.dispatch(
        ["context-rag-llm", "Rin是什么身份？", "--provider", "deepseek"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "DEEPSEEK_API_KEY is not set" in captured.out
    assert "Traceback" not in captured.out


def test_pytest_default_fake_does_not_call_deepseek(monkeypatch):
    calls = []

    def fail_if_called(self):
        calls.append("deepseek")
        raise AssertionError("DeepSeek should not be constructed by default.")

    monkeypatch.setattr(main, "build_llamaindex_nodes", lambda **kwargs: None)
    monkeypatch.setattr(main, "DeepSeekLLMClient", fail_if_called)
    monkeypatch.setattr(
        main,
        "build_context_pack_with_llamaindex",
        lambda *args, **kwargs: {
            "task_context": {"task": args[0]},
            "canon_context": [],
            "draft_reference": [],
            "deprecated_warnings": [],
            "missing_evidence": [],
            "restrictions": [],
            "retrieval_metadata": {},
        },
    )

    exit_code = main.dispatch(["context-rag-llm", "Rin是什么身份？"])

    assert exit_code == 0
    assert calls == []


def test_deepseek_query_rewrite_prompt_requires_json(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    client = DeepSeekLLMClient()

    messages = client._query_rewrite_messages("Rin是什么身份？")
    prompt_text = "\n".join(message["content"] for message in messages)

    assert "Return valid JSON only" in prompt_text
    assert "Do not wrap in markdown" in prompt_text
    assert "original_question" in prompt_text
    assert "rewritten_queries" in prompt_text


def test_deepseek_evidence_prompt_requires_json(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    client = DeepSeekLLMClient()

    messages = client._evidence_selection_messages(
        {
            "question": "Rin是什么身份？",
            "retrieval_plan": {},
            "candidates": [],
        }
    )
    prompt_text = "\n".join(message["content"] for message in messages)

    assert "Return valid JSON only" in prompt_text
    assert "missing_evidence" in prompt_text
    assert "selected_canon_ids" in prompt_text
