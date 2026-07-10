# Normalized Blocks to Context Pack Adapter

## Purpose

This is the second isolated v1 Phase 2 experiment. It validates whether normalized document blocks from the ingestion layer can be adapted into Context Pack-style evidence items without touching the existing v0.4 workflow.

The experiment reads:

```text
experiments/docling_ingestion_eval/sample_outputs/normalized_blocks.jsonl
```

and builds an experimental status-aware context pack using lightweight keyword scoring only.

## Why Normalized Blocks Matter

Normalized blocks are the core handoff object between v1 ingestion and later narrative intelligence layers. They preserve:

- source grounding
- original path
- Canon / Draft / Deprecated / Inspiration status
- section title and heading path
- block type such as text, table, image, or caption
- manifest metadata

If this object is stable, v1 can route the same material into Context Pack, continuity checks, graph extraction, and later narrative production tools without letting Draft, Deprecated, or Inspiration material become Canon.

## How To Run

First generate normalized blocks from the Docling ingestion experiment:

```powershell
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --dry-run
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py
```

Then build one normalized context pack:

```powershell
E:\Desktop\python310\python.exe experiments/normalized_context_adapter/build_context_pack_from_blocks.py "Rin是什么身份？"
```

Generate the comparison report:

```powershell
E:\Desktop\python310\python.exe experiments/normalized_context_adapter/compare_with_legacy_context_pack.py
```

Generated files are written under:

```text
experiments/normalized_context_adapter/sample_outputs/
```

Large generated outputs should stay local and are ignored by Git except `.gitkeep`.

## Legacy Comparison

The comparison script builds normalized-block context packs and compares their source/status coverage against the existing full-context bundle builder. It does not call DeepSeek, does not call a real API, and does not use LlamaIndex retrieval.

The goal is not to prove answer quality. The goal is to test whether normalized blocks can preserve the governance shape required by Context Pack-style evidence.

## Non-goals

This experiment does not:

- modify `main.py`
- modify `src/rag`
- change `ask-full`, `ask-rag`, `context-full`, or `context-rag-llm`
- modify `knowledge_base`
- modify `knowledge_base/import_manifest.json`
- install dependencies
- call DeepSeek
- call any real API
- replace the main workflow
