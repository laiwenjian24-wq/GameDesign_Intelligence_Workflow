# Normalized Context Pack JSON Schema

## Purpose

This isolated v1 experiment turns the normalized Context Pack candidate from Markdown into a stable JSON shape. It does not replace the existing Context Pack, CLI commands, RAG flow, or full-context flow.

The JSON Context Pack is a candidate machine-facing contract for future v1 `chat` and `check-continuity` workflows.

## Why v1 Needs JSON Context Pack

Markdown is useful for humans, but v1 needs a structured object that can be validated, routed, tested, and consumed by workflow code. A JSON Context Pack makes governance rules explicit:

- Canon evidence is separated from Draft, Deprecated, and Inspiration.
- Every evidence item carries `source_file`, `status`, `section_title`, and `source_ref`.
- Missing evidence is explicit instead of implied by absent text.
- Diagnostics can be checked by tests before any answer or continuity decision is produced.

## JSON vs Markdown

JSON Context Pack:

- for machine workflows and LLM pipeline inputs
- supports deterministic validation
- easier to pass into `chat ask`, `check-continuity`, benchmark tests, and future graph extraction
- preserves evidence groups as typed lists

Markdown Context Pack:

- for debug, reports, handoff notes, and human review
- easier to read in terminal or documentation
- useful as a rendering of the JSON object, not the source of truth

Both can coexist: JSON should be the structured contract, while Markdown should be a view over that contract.

## How To Run

First generate normalized blocks:

```powershell
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/docling_parse_sample.py --dry-run
E:\Desktop\python310\python.exe experiments/docling_ingestion_eval/normalize_docling_output.py
```

Then build and validate a JSON Context Pack:

```powershell
E:\Desktop\python310\python.exe experiments/normalized_context_schema/build_json_context_pack.py "Rin是什么身份？"
E:\Desktop\python310\python.exe experiments/normalized_context_schema/validate_context_pack.py
E:\Desktop\python310\python.exe experiments/normalized_context_schema/compare_json_and_markdown_pack.py
```

Outputs are written to:

```text
experiments/normalized_context_schema/sample_outputs/
```

Generated outputs are ignored by Git except `.gitkeep`.

## Relationship To Existing Schema

If `src/context/context_schema.py` exists, it remains the current mainline schema helper. This experiment does not modify it. The candidate schema here is intentionally isolated so it can be compared before any v1 adoption decision.

## Future v1 Integration

Potential later path:

1. Keep normalized ingestion blocks as the input boundary.
2. Build JSON Context Pack as the evidence contract.
3. Render Markdown from JSON for debugging.
4. Feed JSON into v1 `chat ask`.
5. Feed JSON into v1 `check-continuity`.
6. Add benchmark fixtures that validate status separation and missing-evidence behavior.

This experiment does not perform those integrations.
