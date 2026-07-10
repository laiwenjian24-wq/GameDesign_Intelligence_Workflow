# Codex Handoff

## Current Branch

Current branch:

- `feature/v0.4-llm-assisted-rag`

Recent goal:

- Complete the v0.4 experimental comparison layer for STUPID Narrative Workflow.
- Preserve the existing workflow while adding LLM-assisted RAG, Full-context baseline, and answer comparison tools.

## Current Project State

The project has implemented:

- v0.4 LLM-assisted RAG path.
- LlamaIndex BM25 retrieval.
- LLM-assisted query rewrite.
- Evidence selection.
- DeepSeek provider support through environment variable configuration.
- Full-context baseline generation through `context-full`.
- Experimental answer comparison through `ask-full` and `ask-rag`.
- Canon / Draft / Deprecated / Inspiration separation remains intact.
- Context Pack remains the governance core.
- `docs/V1_NARRATIVE_INTELLIGENCE_ARCHITECTURE.md` has been created.
- The v1 project direction has been formally written down.

Most recent test result:

- `56 passed`

Current direction:

- Do not continue adding one-off patches for single failed examples such as Rain / Second Foundation.
- Move from v0.4 RAG experiments toward the v1 Narrative Intelligence Workflow architecture.

## Key Decision

The project should no longer be positioned as a normal RAG project.

New positioning:

- Canon-aware Narrative Intelligence Workflow / Workbench

The core product value is not only retrieval. It is structured narrative governance:

- Canon control
- Draft isolation
- Deprecated conflict handling
- Evidence-grounded reasoning
- Continuity validation
- Narrative production workflow support

## V1 Direction

Core v1 direction:

- v1 is explicitly positioned as a Canon-aware Narrative Intelligence Workflow / Workbench.
- Natural language unified entry point:
  - `main.py chat "..."`
- Docling-based multi-format document parsing.
- LlamaIndex Property Graph / LightRAG as the GraphRAG direction.
- Narrative Bible.
- Scene Function Registry.
- Character Voice Pack.
- Canonization Workflow.
- Tiered Continuity Check.
- Evaluation Benchmark.

The user-facing entry point should be natural language through `main.py chat "..."`.

RAG, GraphRAG, Docling, and LLM providers are infrastructure layers. They are not the product itself. The product is canon-aware narrative governance and production workflow support.

## MVP Scope

v1 MVP should only include:

1. `ingest`
2. `build-index`
3. `chat ask`
4. `check-continuity`

Phase 2 should handle:

- Story continuation
- Art prompt generation
- Streamlit UI

## Important Constraints

- Do not automatically write new material as Canon.
- Do not allow Draft / Deprecated material to override Canon.
- Do not write hardcoded logic around a single failed example.
- The user should not need to use fixed command formats; the system should understand natural language intent.
- Real API keys must only be read from environment variables.
- Do not write API keys into code, docs, tests, logs, or committed files.

## Recommended Next Step

- Create a new `feature/v1-narrative-intelligence-workflow` branch.
- Phase 2 should prioritize a Docling ingestion experiment.
- Do not continue adding single-example patches on `feature/v0.4-llm-assisted-rag`.
- Do not immediately implement GraphRAG as the mainline backend.
- Keep GraphRAG as a parallel experiment for relationship and timeline reasoning.
