# JSON Continuity Check Prototype

## Purpose

This isolated v1 experiment tests whether a continuity checker can make minimal governance decisions from the JSON Context Pack candidate schema.

It does not replace the existing continuity checker and does not connect to `main.py`, `src/rag`, `ask-full`, `ask-rag`, `context-full`, or `context-rag-llm`.

## Why JSON Context Pack

Continuity checking needs structured evidence, not only rendered text. JSON lets the checker inspect:

- whether Canon evidence exists
- whether evidence came from Draft, Deprecated, or Inspiration
- whether `source_file`, `section_title`, and `status` are preserved
- whether a claim requires human review because evidence is missing or ambiguous

This keeps the policy explicit: Draft cannot override Canon, Deprecated cannot be current truth, and Inspiration cannot be factual evidence.

## Current Scope

This is a minimal deterministic prototype. It checks:

- missing Canon evidence
- Deprecated contamination
- Draft overriding Canon
- branch-scope evidence gaps
- insufficient evidence when Canon exists but does not support the extracted claim

It does not check:

- character behavior consistency
- theme, tone, or voice
- complex semantic entailment
- timeline causality
- final narrative truth

When uncertain, it returns `insufficient_evidence` or `NEEDS_REVIEW` instead of pretending to know.

## How To Run

First generate a JSON Context Pack:

```powershell
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --dry-run
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py
E:\Desktop\python310\python.exe experiments/normalized_context_schema/build_json_context_pack.py "Rin是什么身份？"
```

Run one check:

```powershell
E:\Desktop\python310\python.exe experiments/json_continuity_check_eval/check_continuity_from_json_pack.py "Rin是Nexus-7仿生人。"
```

Run sample checks:

```powershell
E:\Desktop\python310\python.exe experiments/json_continuity_check_eval/run_sample_checks.py
```

Generated reports are written to:

```text
experiments/json_continuity_check_eval/sample_outputs/
```

Generated outputs are ignored by Git except `.gitkeep`.

## Future Direction

Later versions can replace the deterministic extractor with LLM-assisted claim extraction, while keeping this JSON policy layer as a validation gate.

Future layers can also consult:

- Character Voice Pack for behavior and speech constraints
- Scene Function Registry for scene-purpose preservation
- Branch Bible for branch-specific state
- Narrative benchmark cases for regression testing

This experiment does not perform those integrations.
