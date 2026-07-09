"""Tests for Narrative QA CLI routing."""

import main


def test_cli_ask_full_routes(monkeypatch):
    calls = []
    monkeypatch.setattr(
        main,
        "run_ask_full",
        lambda question, provider="fake": calls.append((question, provider)),
    )

    exit_code = main.dispatch(["ask-full", "Rin", "identity"])

    assert exit_code == 0
    assert calls == [("Rin identity", "fake")]


def test_cli_ask_full_routes_deepseek_provider(monkeypatch):
    calls = []
    monkeypatch.setattr(
        main,
        "run_ask_full",
        lambda question, provider="fake": calls.append((question, provider)),
    )

    exit_code = main.dispatch(
        ["ask-full", "Rin", "identity", "--provider", "deepseek"]
    )

    assert exit_code == 0
    assert calls == [("Rin identity", "deepseek")]


def test_cli_ask_rag_routes(monkeypatch):
    calls = []
    monkeypatch.setattr(
        main,
        "run_ask_rag",
        lambda question, provider="fake": calls.append((question, provider)),
    )

    exit_code = main.dispatch(["ask-rag", "Rin", "identity"])

    assert exit_code == 0
    assert calls == [("Rin identity", "fake")]


def test_cli_ask_rag_routes_deepseek_provider(monkeypatch):
    calls = []
    monkeypatch.setattr(
        main,
        "run_ask_rag",
        lambda question, provider="fake": calls.append((question, provider)),
    )

    exit_code = main.dispatch(["ask-rag", "Rin", "identity", "--provider", "deepseek"])

    assert exit_code == 0
    assert calls == [("Rin identity", "deepseek")]
