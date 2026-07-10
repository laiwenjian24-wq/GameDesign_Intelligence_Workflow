import main


def test_chat_cli_routes_with_default_fake(capsys):
    exit_code = main.dispatch(["chat", "Rin是什么身份？"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Daily Narrative Assistant" in captured.out
    assert "canon_qa" in captured.out


def test_chat_cli_accepts_provider_fake(capsys):
    exit_code = main.dispatch(["chat", "Rin是什么身份？", "--provider", "fake"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "fake" in captured.out


def test_existing_context_full_command_still_dispatches(monkeypatch):
    called = {}

    def fake_run_context_full(question):
        called["question"] = question

    monkeypatch.setattr(main, "run_context_full", fake_run_context_full)
    exit_code = main.dispatch(["context-full", "Rin是什么身份？"])
    assert exit_code == 0
    assert called["question"] == "Rin是什么身份？"
