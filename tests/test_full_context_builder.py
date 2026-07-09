"""Tests for the full-context baseline bundle builder."""

import json

import main
from src.context.full_context_builder import (
    build_full_context_bundle,
    format_full_context_bundle_markdown,
)


def _write_source(tmp_path, filename, text):
    path = tmp_path / filename
    path.write_text(text, encoding="utf-8")
    return path


def _write_manifest(tmp_path, items):
    manifest_path = tmp_path / "import_manifest.json"
    manifest_path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest_path


def _manifest_item(path, status, asset_type="test"):
    return {
        "file_path": str(path),
        "asset_type": asset_type,
        "status": status,
        "tags": [status],
        "reason": f"{status} reason",
        "expected_usage": f"{status} usage",
    }


def test_full_context_groups_by_status(tmp_path):
    canon = _write_source(tmp_path, "canon.md", "Canon fact.")
    draft = _write_source(tmp_path, "draft.md", "Draft reference.")
    deprecated = _write_source(tmp_path, "deprecated.md", "Deprecated conflict.")
    inspiration = _write_source(tmp_path, "inspiration.md", "Inspiration only.")
    manifest_path = _write_manifest(
        tmp_path,
        [
            _manifest_item(canon, "canon"),
            _manifest_item(draft, "draft"),
            _manifest_item(deprecated, "deprecated"),
            _manifest_item(inspiration, "inspiration"),
        ],
    )

    bundle = build_full_context_bundle("Rin是什么身份？", manifest_path=manifest_path)

    assert bundle["groups"]["canon"][0]["text"] == "Canon fact."
    assert bundle["groups"]["draft"][0]["text"] == "Draft reference."
    assert bundle["groups"]["deprecated"][0]["text"] == "Deprecated conflict."
    assert bundle["groups"]["inspiration"][0]["text"] == "Inspiration only."
    assert len(bundle["source_list"]) == 4


def test_full_context_includes_llm_instructions(tmp_path):
    canon = _write_source(tmp_path, "canon.md", "Canon fact.")
    manifest_path = _write_manifest(tmp_path, [_manifest_item(canon, "canon")])

    bundle = build_full_context_bundle("Rin是什么身份？", manifest_path=manifest_path)
    markdown = format_full_context_bundle_markdown(bundle)

    assert "Canon is the only authoritative fact source." in markdown
    assert "Draft can be used only as writing reference" in markdown
    assert "Deprecated can be used only as historical conflict evidence" in markdown
    assert "Inspiration can be used only as thematic reference" in markdown
    assert "If Canon does not contain enough evidence" in markdown
    assert "Every answer must list the source files used." in markdown


def test_full_context_does_not_modify_files(tmp_path):
    canon = _write_source(tmp_path, "canon.md", "Canon fact.")
    manifest_path = _write_manifest(tmp_path, [_manifest_item(canon, "canon")])
    source_before = canon.read_text(encoding="utf-8")
    manifest_before = manifest_path.read_text(encoding="utf-8")

    build_full_context_bundle("Rin是什么身份？", manifest_path=manifest_path)

    assert canon.read_text(encoding="utf-8") == source_before
    assert manifest_path.read_text(encoding="utf-8") == manifest_before
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "canon.md",
        "import_manifest.json",
    ]


def test_context_full_cli_routes(monkeypatch, capsys):
    calls = []

    def fake_build_bundle(question):
        calls.append(("build_full", question))
        return {
            "question": question,
            "instructions": ["Canon is the only authoritative fact source."],
            "groups": {
                "canon": [],
                "draft": [],
                "deprecated": [],
                "inspiration": [],
            },
            "source_list": [],
            "estimated_character_count": 0,
            "rough_token_estimate": 0,
        }

    monkeypatch.setattr(main, "build_full_context_bundle", fake_build_bundle)

    exit_code = main.dispatch(["context-full", "Rin", "identity"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert calls == [("build_full", "Rin identity")]
    assert "# Full-context Bundle" in captured.out
    assert "## Instructions for LLM" in captured.out
