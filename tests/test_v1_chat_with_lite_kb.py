import main
from src.v1.chat.daily_assistant import run_daily_assistant
from src.v1.kb.lite_index import build_lite_index, save_lite_index


def _kb_path(tmp_path):
    canon = tmp_path / "rin.md"
    canon.write_text("# Rin\n\nRin is Nexus-7 android.\n\nBranch B: Rin left leg injury.", encoding="utf-8")
    deprecated = tmp_path / "old.md"
    deprecated.write_text("# Old Kite\n\nDeprecated old draft says Rin right leg injury.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    manifest.write_text(
        "["
        + '{"file_path":"' + str(canon).replace("\\", "\\\\") + '","status":"canon","asset_type":"character","tags":["Rin","Branch B"]},'
        + '{"file_path":"' + str(deprecated).replace("\\", "\\\\") + '","status":"deprecated","asset_type":"deprecated","tags":["Rin"]}'
        + "]",
        encoding="utf-8",
    )
    kb = build_lite_index([tmp_path], manifest_path=manifest)
    output = tmp_path / "processed" / "v1_lite_kb.json"
    save_lite_index(kb, output)
    return output


def test_chat_kb_canon_qa_shows_evidence_snippets(tmp_path):
    kb = _kb_path(tmp_path)
    response = run_daily_assistant("Rin是什么身份？", provider="fake", kb_path=str(kb))

    assert "Evidence Snippets" in response.answer_markdown
    assert "rin.md" in response.answer_markdown


def test_chat_kb_continuity_check_shows_evidence_snippets(tmp_path):
    kb = _kb_path(tmp_path)
    response = run_daily_assistant(
        "Branch B中Rin右腿受伤，这样能用吗？",
        provider="fake",
        kb_path=str(kb),
    )

    assert "Evidence Snippets" in response.answer_markdown
    assert "old.md" in response.answer_markdown or "rin.md" in response.answer_markdown


def test_chat_kb_does_not_call_real_api_without_deepseek(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    kb = _kb_path(tmp_path)
    response = run_daily_assistant("Rin是什么身份？", provider="fake", kb_path=str(kb))

    assert response.provider == "fake"


def test_chat_deepseek_missing_key_fallback_with_kb(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    kb = _kb_path(tmp_path)
    response = run_daily_assistant("Rin是什么身份？", provider="deepseek", kb_path=str(kb))

    assert response.provider == "fake"
    assert response.debug_task_plan["fallback_reason"]


def test_ingest_lite_cli_and_chat_kb_cli(tmp_path, capsys):
    source = tmp_path / "rin.md"
    source.write_text("# Rin\n\nRin is Nexus-7 android.", encoding="utf-8")
    output = tmp_path / "processed" / "v1_lite_kb.json"

    exit_code = main.dispatch(["ingest-lite", "--input", str(tmp_path), "--output", str(output)])
    assert exit_code == 0
    assert output.exists()

    exit_code = main.dispatch(["chat", "Rin是什么身份？", "--provider", "fake", "--kb", str(output)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Evidence Snippets" in captured.out
