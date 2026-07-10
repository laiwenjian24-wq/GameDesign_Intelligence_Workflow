# Docling Ingestion Experiment

## Purpose

This is an isolated v1 Narrative Intelligence Workflow ingestion-layer experiment. It tests whether Docling can parse multi-format narrative project sources into normalized document blocks while preserving source grounding, section structure, manifest metadata, and Canon / Draft / Deprecated / Inspiration status.

This experiment does not replace the existing v0.4 workflow.

## Why Ingestion Before GraphRAG

v1 depends on trustworthy source material before relationship or graph reasoning can be useful. GraphRAG can help later with relationships, timelines, factions, causality, and branch state, but graph edges are only valuable when extracted from well-grounded, status-aware source blocks.

The immediate risk is not graph traversal. The immediate risk is losing source file, section, status, or provenance during multi-format parsing. This experiment validates that foundation first.

## Docling's Place In v1

Docling belongs in the Document Understanding Layer:

```text
raw project sources
-> Docling / dry-run parser
-> normalized markdown/json-like blocks
-> status-aware ingestion review
-> Context Pack / index / future graph experiments
```

Docling is not the product, not the retrieval backend, and not a canonization authority. It is a candidate parser that may feed the existing governance model.

## Target Formats

Initial target formats:

- `md`
- `docx`
- `pdf`
- `jpg`
- `png`

Later candidates:

- `pptx`
- `xlsx`

## Dry-run Mode

Dry-run mode does not require Docling and does not call any API.

```powershell
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --dry-run
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/compare_ingestion_quality.py
```

Dry-run mode reads `knowledge_base/import_manifest.json`, selects a small sample, records manifest metadata, and reads local Markdown text only when the source file is available.

## Real Docling Parse

If Docling is already installed, run:

```powershell
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --real
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/compare_ingestion_quality.py
```

If Docling is not installed, the script exits cleanly with a clear message. This experiment does not install heavy dependencies by default.

## Output Files

Generated outputs are written under:

```text
experiments/docling_ingestion_eval/sample_outputs/
```

Large parse outputs should stay local and should not be committed. The repository ignores generated files in this folder except `.gitkeep`.

Expected generated files:

- `docling_parse_results.json`
- `normalized_blocks.jsonl`
- `docling_ingestion_eval_report.md`

## Quality Evaluation

The comparison report checks:

- whether `status` is preserved
- whether `source_file` is preserved
- whether heading and section information is preserved
- whether tables can be recognized or extended
- whether image and caption blocks can be represented
- whether Canon / Draft / Deprecated / Inspiration status categories survive
- whether normalized blocks are suitable for later Context Pack and GraphRAG use

## Non-goals

This experiment does not:

- modify `main.py`
- modify `src/rag`
- change `ask-full`, `ask-rag`, `context-full`, or `context-rag-llm`
- modify original `knowledge_base` materials
- modify `knowledge_base/import_manifest.json`
- call DeepSeek
- call any real API
- automatically canonize imported material
