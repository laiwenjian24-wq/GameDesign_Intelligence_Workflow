import json
from pathlib import Path

from experiments.docling_ingestion_eval.compare_ingestion_quality import run as compare_run
from experiments.docling_ingestion_eval.docling_parse_sample import run as parse_run
from experiments.docling_ingestion_eval.normalize_docling_output import run as normalize_run


def _write_manifest(tmp_path: Path) -> Path:
    canon = tmp_path / "STUPID游戏世界观设定集.md"
    canon.write_text("# 世界观\n\nCanon paragraph.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n", encoding="utf-8")
    draft = tmp_path / "故事大纲与角色设定.md"
    draft.write_text("# 角色\n\nDraft paragraph.\n", encoding="utf-8")
    deprecated = tmp_path / "任务设计_风筝.md"
    deprecated.write_text("# 风筝\n\nDeprecated paragraph.\n", encoding="utf-8")
    inspiration = tmp_path / "visual.png"
    inspiration.write_bytes(b"not a real image")
    manifest = [
        {
            "file_path": str(canon),
            "asset_type": "worldbuilding",
            "status": "canon",
            "confidence": "high",
            "tags": ["world"],
        },
        {
            "file_path": str(draft),
            "asset_type": "character",
            "status": "draft",
            "confidence": "medium",
            "tags": ["character"],
        },
        {
            "file_path": str(deprecated),
            "asset_type": "branch",
            "status": "deprecated",
            "confidence": "high",
            "tags": ["kite"],
        },
        {
            "file_path": str(inspiration),
            "asset_type": "visual_reference",
            "status": "inspiration",
            "confidence": "medium",
            "tags": ["image"],
        },
    ]
    manifest_path = tmp_path / "import_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return manifest_path


def test_docling_ingestion_dry_run_without_docling(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    output_path = tmp_path / "sample_outputs" / "docling_parse_results.json"

    parse_run(manifest_path=manifest_path, output_path=output_path, real=False, limit=4)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["results"]
    assert {item["parser"] for item in payload["results"]} == {"dry-run"}


def test_normalized_blocks_include_required_governance_fields(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    parse_output = tmp_path / "sample_outputs" / "docling_parse_results.json"
    blocks_output = tmp_path / "sample_outputs" / "normalized_blocks.jsonl"

    parse_run(manifest_path=manifest_path, output_path=parse_output, real=False, limit=4)
    normalize_run(input_path=parse_output, output_path=blocks_output)

    blocks = [
        json.loads(line)
        for line in blocks_output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert blocks
    for block in blocks:
        assert block["source_file"]
        assert block["status"]
        assert block["section_title"]
        assert block["block_type"]


def test_experiment_does_not_modify_manifest_or_sources(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    before_manifest = manifest_path.read_text(encoding="utf-8")
    source_snapshots = {
        path: path.read_bytes()
        for path in tmp_path.iterdir()
        if path.name != "sample_outputs" and path.is_file()
    }
    parse_output = tmp_path / "sample_outputs" / "docling_parse_results.json"
    blocks_output = tmp_path / "sample_outputs" / "normalized_blocks.jsonl"
    report_output = tmp_path / "sample_outputs" / "docling_ingestion_eval_report.md"

    parse_run(manifest_path=manifest_path, output_path=parse_output, real=False, limit=4)
    normalize_run(input_path=parse_output, output_path=blocks_output)
    compare_run(blocks_path=blocks_output, manifest_path=manifest_path, report_path=report_output)

    assert manifest_path.read_text(encoding="utf-8") == before_manifest
    for path, content in source_snapshots.items():
        assert path.read_bytes() == content
    assert "Status Preservation" in report_output.read_text(encoding="utf-8")
