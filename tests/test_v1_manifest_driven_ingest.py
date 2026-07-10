import json

from main import dispatch
from src.v1.ingestion.manifest_status_resolver import inspect_manifest
from src.v1.kb.lite_index import build_lite_index, build_lite_index_from_manifest


def _write_manifest(path, items):
    path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


def test_from_manifest_reads_manifest_fixture_files(tmp_path):
    source = tmp_path / "story.md"
    source.write_text("# Story\n\nRin is Nexus-7.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    _write_manifest(
        manifest,
        [{"file_path": str(source), "status": "canon", "asset_type": "character"}],
    )

    kb = build_lite_index_from_manifest(manifest)

    assert kb.blocks
    assert kb.status_counts.get("canon", 0) > 0
    assert kb.metadata["manifest_driven_ingest"]["enabled"] is True
    assert kb.metadata["manifest_driven_ingest"]["files_loaded"] == 1


def test_from_manifest_block_status_comes_from_manifest_entry(tmp_path):
    source = tmp_path / "note.md"
    source.write_text("# Note\n\nDraft-only detail.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    _write_manifest(manifest, [{"file_path": str(source), "status": "draft"}])

    kb = build_lite_index_from_manifest(manifest)

    assert {block["status"] for block in kb.blocks} == {"draft"}
    assert {
        block["metadata"]["status_resolution_method"] for block in kb.blocks
    } == {"manifest_entry_direct"}


def test_from_manifest_missing_file_enters_diagnostics(tmp_path):
    missing = tmp_path / "missing.md"
    manifest = tmp_path / "import_manifest.json"
    _write_manifest(manifest, [{"file_path": str(missing), "status": "canon"}])

    kb = build_lite_index_from_manifest(manifest)
    metadata = kb.metadata["manifest_driven_ingest"]

    assert kb.blocks == []
    assert metadata["files_missing"] == 1
    assert metadata["missing_files"][0]["resolved_path"].endswith("missing.md")
    assert kb.metadata["warnings"]


def test_from_manifest_handles_windows_backslash_paths(tmp_path):
    source = tmp_path / "branch.md"
    source.write_text("# Branch\n\nMouse injury note.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    _write_manifest(
        manifest,
        [{"file_path": str(source).replace("/", "\\"), "status": "deprecated"}],
    )

    kb = build_lite_index_from_manifest(manifest)

    assert kb.status_counts.get("deprecated", 0) > 0


def test_manifest_doctor_marks_suspected_mojibake_without_fixing(tmp_path):
    manifest = tmp_path / "import_manifest.json"
    mojibake_path = r"E:\desktop\stupid鍒涗綔\绔犺妭.md"
    _write_manifest(manifest, [{"file_path": mojibake_path, "status": "canon"}])

    report = inspect_manifest(manifest)

    assert report["suspected_mojibake_count"] == 1
    assert report["entries"][0]["suspected_mojibake"] is True
    assert report["entries"][0]["display_path"] == mojibake_path


def test_manifest_doctor_cli_outputs_diagnostics(tmp_path, capsys):
    source = tmp_path / "rin.md"
    source.write_text("# Rin", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    _write_manifest(manifest, [{"file_path": str(source), "status": "canon"}])

    exit_code = dispatch(["manifest-doctor", "--manifest", str(manifest)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Manifest entries loaded: 1" in output
    assert "Status counts:" in output
    assert "Existing path count: 1" in output


def test_ingest_lite_from_manifest_cli_writes_output(tmp_path, capsys):
    source = tmp_path / "rin.md"
    source.write_text("# Rin\n\nRin is Nexus-7.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    output = tmp_path / "processed" / "kb.json"
    _write_manifest(manifest, [{"file_path": str(source), "status": "canon"}])

    exit_code = dispatch(
        [
            "ingest-lite",
            "--from-manifest",
            str(manifest),
            "--output",
            str(output),
        ]
    )
    text = capsys.readouterr().out

    assert exit_code == 0
    assert output.exists()
    assert "Manifest-driven ingest: enabled" in text
    assert "Status counts: {'canon':" in text


def test_existing_input_manifest_behavior_still_works(tmp_path):
    source = tmp_path / "canon.md"
    source.write_text("# Canon\n\nCanon note.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    _write_manifest(manifest, [{"file_path": "canon.md", "status": "canon"}])

    kb = build_lite_index([tmp_path], manifest_path=manifest, include_ext=[".md"])

    assert kb.status_counts.get("canon", 0) > 0
    assert kb.metadata["manifest_status_diagnostics"]["matched_file_count"] >= 1
