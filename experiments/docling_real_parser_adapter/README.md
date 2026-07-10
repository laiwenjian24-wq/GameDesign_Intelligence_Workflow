# Docling Real Parser Adapter Experiment

## Purpose

This isolated Phase 4.1 experiment tests whether real Docling parser output can be adapted into the mainline v1 `NormalizedBlock` schema.

It does not replace v0.4 ingestion, retrieval, QA, or continuity behavior. It does not implement production ingest.

## Why Phase 3.2 Was Skipped

Phase 3.2 fixture-loader infrastructure was skipped because this is a personal portfolio project, not a commercial platform. The v1 skeleton, schemas, validator, fixtures, and passing tests already demonstrate the core engineering governance value.

The higher-value next step is proving that v1 ingestion can accept real multi-format parser output.

## Position In v1

Docling belongs in the v1 Document Understanding / ingestion layer:

```text
project source file
-> Docling parser
-> parser summary / markdown export
-> src.v1.ingestion.NormalizedBlock
-> JSON Context Pack
```

Docling is a parser candidate. It is not a retrieval backend, not a Canon authority, and not a replacement for Context Pack governance.

## Install Docling

Docling is not installed by this experiment. To install it manually:

```powershell
E:\Desktop\python310\python.exe -m pip install docling
```

If Docling is not installed, the script prints `docling_not_installed` and exits cleanly.

## Run Single-file Parse

```powershell
E:\Desktop\python310\python.exe experiments/docling_real_parser_adapter/docling_real_parse.py --input "path/to/file.pdf"
E:\Desktop\python310\python.exe experiments/docling_real_parser_adapter/docling_to_normalized_blocks.py
```

## Run Manifest Sample Parse

```powershell
E:\Desktop\python310\python.exe experiments/docling_real_parser_adapter/docling_real_parse.py --from-manifest --limit 3
E:\Desktop\python310\python.exe experiments/docling_real_parser_adapter/docling_to_normalized_blocks.py
```

The parser reads source files only. It does not modify source files or `import_manifest.json`.

## Compare With Dry-run

```powershell
E:\Desktop\python310\python.exe experiments/docling_real_parser_adapter/compare_real_vs_dry_run.py
```

Comparison report:

```text
experiments/docling_real_parser_adapter/sample_outputs/real_vs_dry_run_report.md
```

## Non-goals

This experiment does not:

- modify `main.py`
- modify `src/rag`
- modify `knowledge_base`
- modify `import_manifest.json`
- call DeepSeek or any real API
- connect GraphRAG
- implement production ingest
- implement production chat
- implement production check-continuity
