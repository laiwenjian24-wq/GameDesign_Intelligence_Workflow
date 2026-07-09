"""Tests for main.py CLI routing."""

import main


def test_unknown_command_should_not_run_ingestion(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(main, "run_ingestion", lambda: calls.append("ingestion"))

    exit_code = main.dispatch(["abc"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert calls == []
    assert "Unknown command: abc" in captured.out
    assert "- context-rag" in captured.out


def test_context_rag_command_routes_to_llamaindex_context_builder(monkeypatch, capsys):
    calls = []

    monkeypatch.setattr(
        main,
        "build_llamaindex_nodes",
        lambda **kwargs: calls.append(("build_nodes", kwargs)),
    )

    def fake_build_context(task, top_k, index_dir):
        calls.append(("build_context", task, top_k, index_dir))
        return {
            "task_context": {"task": task},
            "canon_context": [
                {
                    "source_file": "rin_canon.md",
                    "status": "canon",
                    "score": 1.25,
                    "retrieval_mode": "bm25",
                    "used_real_llamaindex": True,
                    "fallback": False,
                    "excerpt": "Rin identity is Nexus-7.",
                    "text": "Rin identity is Nexus-7.",
                    "reason_used": "test",
                }
            ],
            "draft_reference": [],
            "deprecated_warnings": [],
            "missing_evidence": [],
            "restrictions": ["canon: Authoritative evidence."],
            "retrieval_metadata": {
                "retrieval_mode": "bm25",
                "used_real_llamaindex": True,
                "fallback": False,
            },
        }

    monkeypatch.setattr(main, "build_context_pack_with_llamaindex", fake_build_context)

    exit_code = main.dispatch(["context-rag", "Rin", "identity"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert calls[0][0] == "build_nodes"
    assert calls[1][0] == "build_context"
    assert calls[1][1] == "Rin identity"
    assert calls[1][2] == 8
    assert "## Canon Context" in captured.out
    assert "rin_canon.md" in captured.out
    assert "score: 1.25" in captured.out
    assert "retrieval_mode: bm25" in captured.out
    assert "used_real_llamaindex: True" in captured.out


def test_existing_context_and_check_commands_still_route(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "run_context", lambda task: calls.append(("context", task)))
    monkeypatch.setattr(main, "run_check", lambda task: calls.append(("check", task)))

    assert main.dispatch(["context", "Rin", "identity"]) == 0
    assert main.dispatch(["check", "Rin", "identity"]) == 0

    assert calls == [
        ("context", "Rin identity"),
        ("check", "Rin identity"),
    ]
