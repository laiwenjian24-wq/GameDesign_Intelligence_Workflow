# V1 Experiment Consolidation

## 1. Purpose

This document consolidates the isolated v1 Narrative Intelligence Workflow experiments completed so far. Its purpose is to clarify what the experiments proved, how the candidate data flow works, and which parts are stable enough to consider for mainline migration.

This document is a migration-planning artifact. It does not replace the existing v0.4 workflow.

## 2. Completed Experiments

### 1. docling_ingestion_eval

Purpose:

- Test whether a v1 ingestion layer can produce normalized document blocks while preserving source grounding and governance metadata.
- Keep Docling evaluation isolated from the existing v0.4 flow.

Input:

- `knowledge_base/import_manifest.json`
- Selected project source files from the manifest.
- Dry-run parser output when Docling is not installed.

Output:

- `experiments/docling_ingestion_eval/sample_outputs/normalized_blocks.jsonl`

Conclusion:

- The dry-run path can preserve `source_file`, `original_path`, `status`, `section_title`, `heading_path`, `block_type`, and manifest metadata.
- It can represent Canon / Draft / Deprecated / Inspiration status in normalized blocks.
- It can detect basic Markdown section and table structure.
- This validates the normalized block shape as a candidate ingestion handoff object, but it does not prove real Docling quality for PDF, image, docx, or other formats.

Modified mainline:

- No.

### 2. normalized_context_adapter

Purpose:

- Test whether normalized blocks can be converted into Context Pack-style evidence items.
- Produce a Markdown Context Pack for human-readable debugging.

Input:

- `normalized_blocks.jsonl`

Output:

- Evidence items with source, status, section, excerpt, source reference, and status policy.
- Markdown Context Pack grouped by Canon / Draft / Deprecated / Inspiration.

Conclusion:

- The adapter can preserve `status`, `source_file`, and `section_title`.
- It can keep Canon / Draft / Deprecated / Inspiration in separate groups.
- It confirms that normalized blocks can feed the Context Pack idea without tying the workflow to a specific RAG backend.

Modified mainline:

- No.

### 3. normalized_context_schema

Purpose:

- Turn the normalized Context Pack candidate from Markdown into a machine-readable JSON schema.

Input:

- Normalized blocks through the adapter layer.

Output:

- `context_pack.json`
- Validation report.
- JSON vs Markdown comparison report.

Conclusion:

- JSON Context Pack is suitable as a v1 evidence contract candidate.
- It makes `canon_context`, `draft_reference`, `deprecated_warnings`, `inspiration_reference`, `missing_evidence`, `diagnostics`, and metadata explicit.
- JSON is better for workflow execution and validation; Markdown is better for debug and review.

Modified mainline:

- No.

### 4. json_continuity_check_eval

Purpose:

- Test whether a continuity checker can make minimal governance decisions from JSON Context Pack structure.

Input:

- New content string.
- Candidate JSON Context Pack.

Output:

- Markdown continuity check report.
- Extracted minimal claims.
- Issues such as `missing_canon_evidence`, `deprecated_contamination`, `draft_overrides_canon`, `branch_state_conflict`, and `insufficient_evidence`.

Conclusion:

- JSON Context Pack can support a minimal rule-based governance check.
- The prototype correctly enforces that Deprecated cannot be current truth, Draft cannot override Canon, and Inspiration cannot be factual evidence.
- This is not a full semantic continuity checker. It does not solve character behavior, theme, tone, causality, or robust branch-state reasoning.

Modified mainline:

- No.

### 5. continuity_benchmark_fixtures

Purpose:

- Freeze initial continuity governance expectations as benchmark fixtures.
- Provide a regression safety net before future v1 work adds LLM claim extraction, real Docling parsing, GraphRAG, or mainline integration.

Input:

- `fixtures/continuity_cases.json`
- Candidate JSON Context Pack.

Output:

- `continuity_benchmark_report.md`

Current result:

- 8 cases.
- 100% pass.

Conclusion:

- The benchmark captures an initial governance baseline.
- It verifies status policy behavior, not full semantic intelligence.
- The benchmark and prototype have evolved together, so this should be treated as an initial safety net rather than proof that real continuity checking is solved.

Modified mainline:

- No.

## 3. Candidate V1 Data Flow

Candidate flow:

```text
Project files
-> Docling / dry-run parser
-> normalized_blocks.jsonl
-> evidence_adapter
-> JSON Context Pack
-> continuity checker
-> benchmark report
```

The v1 mainline should center on JSON Context Pack as the evidence protocol. It should define what evidence is, what status it carries, where it came from, and how it may be used.

Markdown Context Pack should remain a debug and report rendering. It is useful for humans, but it should not be the source-of-truth workflow object.

The Context Pack protocol is more core than any specific RAG backend. LlamaIndex, Docling, Haystack, GraphRAG, or other tools should feed or consume the protocol. They should not bypass it.

## 4. What Can Move Toward Mainline

The following parts are stable enough to consider for mainline migration:

- Normalized block schema.
- Evidence item adapter.
- JSON Context Pack schema.
- Context Pack validation.
- Source/status policy.
- Benchmark fixtures as a regression safety net.

These should move only with focused tests and without replacing v0.4 commands.

## 5. What Should Stay Experimental

The following should remain experimental for now:

- Dry-run parser implementation details.
- Simple keyword scoring.
- Deterministic `simple_claim_extractor`.
- Current continuity prototype rules.
- `sample_outputs`.
- GraphRAG backend.
- Real Docling parser path until tested on representative PDF, image, docx, and mixed-format inputs.

These components are useful for proving architecture shape, but they are not production-quality workflow logic.

## 6. Risks

- The benchmark currently evolved together with the prototype, so it may overfit the current rule behavior.
- Simple claim extraction is too weak for real narrative continuity checking.
- Keyword matching does not represent real retrieval quality.
- Branch and state judgment remains insufficient.
- Character behavior, tone, theme, and scene-function conflicts are not covered.
- `normalized_blocks` currently mostly reflects Markdown dry-run behavior and does not prove real PDF, image, or docx parsing quality.
- GraphRAG relationship extraction can hallucinate edges unless every edge is source-cited and governed by Canon status.

## 7. Recommended Next Step

The next step should not be GraphRAG and should not be UI.

Recommended next phase:

```text
Phase 3: Mainline v1 skeleton
```

Goal:

- Add a v1 module skeleton without replacing v0.4.

Candidate structure:

```text
src/v1/
  ingestion/
  context/
  continuity/
  benchmark/
```

Prioritize migrating stable content:

- Schema.
- Status policy.
- JSON Context Pack validation.
- Benchmark fixture runner.

Do not migrate yet:

- Simple keyword retrieval.
- `simple_claim_extractor` as production logic.
- Experimental scoring.

The first mainline step should be boring and structural: create a stable namespace, tests, and contracts. Retrieval and generation behavior can remain experimental until the contracts are reliable.

## 8. Mainline Migration Rules

- Every module moved into mainline must have tests.
- Migration must not break v0.4 commands.
- New material must not be automatically canonized.
- Draft / Deprecated / Inspiration must not enter `canon_context`.
- Real API calls must be opt-in.
- `sample_outputs` must not be committed.
- Full pytest must be run after every migration step.

## 9. Portfolio Value

These experiments show that the project is not only a RAG demo.

They demonstrate:

- Evidence contract design.
- Canon-aware governance.
- Source-grounded narrative workflow architecture.
- Continuity regression benchmarking.
- A practical path from narrative design needs to engineering workflow.

The strongest portfolio framing is:

> A canon-aware AI narrative workflow for game development that turns heterogeneous project materials into governed evidence packs, validates continuity risks, and protects Canon / Draft / Deprecated / Inspiration boundaries before retrieval or generation can influence production decisions.
