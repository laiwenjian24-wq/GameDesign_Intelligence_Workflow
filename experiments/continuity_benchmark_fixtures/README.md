# Continuity Benchmark Fixtures

## Purpose

This isolated v1 experiment turns continuity-check expectations into JSON fixtures and a deterministic benchmark runner.

The benchmark is designed to prevent governance regressions when v1 later adds Docling real parsing, LLM claim extraction, GraphRAG, or a natural-language `chat` entry point.

It does not replace the existing workflow or continuity checker.

## What This Benchmark Measures

The benchmark is not testing whether a model is clever. It is testing whether the workflow preserves narrative governance rules:

- Canon is the only current-truth source.
- Draft cannot override Canon.
- Deprecated cannot be used as current truth.
- Inspiration cannot be used as fact.
- Missing or ambiguous Canon evidence should produce review/insufficient-evidence behavior, not a confident pass.

## Files

```text
fixtures/continuity_cases.json
benchmark_schema.py
benchmark_runner.py
report_writer.py
sample_outputs/
```

## How To Run

First generate the JSON Context Pack candidate:

```powershell
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --dry-run
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py
E:\Desktop\python310\python.exe experiments/normalized_context_schema/build_json_context_pack.py "Rin是什么身份？"
```

Then run the benchmark:

```powershell
E:\Desktop\python310\python.exe experiments/continuity_benchmark_fixtures/benchmark_runner.py
```

Report output:

```text
experiments/continuity_benchmark_fixtures/sample_outputs/continuity_benchmark_report.md
```

Generated reports are ignored by Git except `.gitkeep`.

## Adding New Fixtures

Add a case to `fixtures/continuity_cases.json` with:

- `case_id`
- `category`
- `input_text`
- `expected_decision`
- `allowed_decisions`
- `expected_issue_types`
- `required_evidence_statuses`
- `forbidden_evidence_statuses`
- `expected_source_policy`
- `notes`

Use `allowed_decisions` when a prototype may validly return either `NEEDS_REVIEW` or `FAIL`. Do not make `PASS` acceptable for cases where Canon support is missing or where Draft/Deprecated/Inspiration is being used as current truth.

## Non-goals

This benchmark does not test:

- character behavior
- theme or tone
- complex semantic entailment
- final authorial canon decisions
- LLM quality

Those belong in later v1 benchmark layers after the governance baseline is stable.
