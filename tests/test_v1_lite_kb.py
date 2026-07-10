from src.v1.kb.lite_index import build_lite_index, load_lite_index, save_lite_index
from src.v1.kb.lite_retriever import retrieve_lite_evidence


def test_lite_index_saves_and_loads(tmp_path):
    source = tmp_path / "rin.md"
    source.write_text("# Rin\n\nRin is Nexus-7 android.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    manifest.write_text(
        '[{"file_path":"' + str(source).replace("\\", "\\\\") + '","status":"canon","asset_type":"character","tags":["Rin"]}]',
        encoding="utf-8",
    )
    output = tmp_path / "processed" / "v1_lite_kb.json"

    kb = build_lite_index([source], manifest_path=manifest)
    save_lite_index(kb, output)
    loaded = load_lite_index(output)

    assert loaded.blocks
    assert loaded.status_counts["canon"] >= 1


def test_lite_retriever_returns_keyword_evidence(tmp_path):
    source = tmp_path / "rin.md"
    source.write_text("# Rin\n\nRin is Nexus-7 android.", encoding="utf-8")
    manifest = tmp_path / "import_manifest.json"
    manifest.write_text(
        '[{"file_path":"' + str(source).replace("\\", "\\\\") + '","status":"canon","asset_type":"character","tags":["Rin"]}]',
        encoding="utf-8",
    )

    kb = build_lite_index([source], manifest_path=manifest)
    evidence = retrieve_lite_evidence("Rin是什么身份？", kb)

    assert evidence
    assert evidence[0]["source_file"] == "rin.md"
    assert evidence[0]["status"] == "canon"
    assert evidence[0]["score"] > 0
