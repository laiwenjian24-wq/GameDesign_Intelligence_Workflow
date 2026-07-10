# Build vs Open-source Boundary

## 1. Purpose

This document prevents the project from drifting into unbounded infrastructure rewrites.

The project should use mature open-source tools or external backends for general AI infrastructure. The in-house work should stay focused on the game writing and narrative design problem: a Canon-aware narrative workflow for managing source authority, continuity, branch state, and production briefs.

The project should not build generic AI engineering capability from scratch when reliable tools already exist for document parsing, OCR, knowledge bases, vector search, LLM evaluation, UI, or image generation pipelines.

## 2. Core Principle

External tools are replaceable infrastructure.

`src/v1` is the narrative governance layer.

All external backends must pass through adapters that output `EvidenceItem`, `NormalizedBlock`, or Context Pack-compatible structures.

External tools cannot become Canon authority. They may parse, retrieve, rank, summarize, or display material, but they must not decide whether material is Canon.

## 3. Use Mature Open-source For

### Multi-format ingestion / OCR / PDF layout

Preferred:

- RAGFlow / DeepDoc

Fallback:

- MinerU
- Marker
- Unstructured
- Docling if installation is stable

Decision:

Do not build a custom parser stack unless all candidates fail on representative project samples.

### Knowledge base / retrieval

Preferred:

- RAGFlow as external backend

Fallback:

- Existing LlamaIndex pipeline
- Qdrant or Chroma for vector DB

Decision:

Do not build a vector database or retrieval engine from scratch.

### LLM provider gateway

Current:

- Simple DeepSeek adapter is acceptable.

Future:

- LiteLLM if supporting multiple providers becomes necessary.

Decision:

Do not build a custom multi-provider gateway.

### UI

Current:

- Streamlit

Decision:

Do not rewrite the frontend.

Do not migrate to Dify as the project core.

Dify may only be used as a comparison or demo shell.

### Evaluation

Current:

- `pytest` fixtures

Future:

- DeepEval or Ragas
- Phoenix or Langfuse for tracing/observability if needed

Decision:

Do not invent a full LLM evaluation platform.

### Image generation pipeline

Future:

- ComfyUI or InvokeAI

Decision:

The current project only generates prompt briefs.

Do not implement image generation now.

### Workflow orchestration

Current:

- Simple `task_router`

Future:

- Haystack only if routing or pipeline complexity grows.
- LangGraph only if long-running stateful agents become necessary.

Decision:

Do not introduce an orchestration framework now.

## 4. Build In-house For

### Canon-aware source governance

- Status policy.
- Canon / Draft / Deprecated / Inspiration rules.
- Unknown status requires review.

### Narrative continuity

- Branch-state conflict.
- Deprecated contamination.
- Missing evidence.
- Character/state consistency.

### Narrative task layer

- Canon QA output contract.
- Continuity Check output contract.
- Story Brief structure.
- Art Prompt Brief structure.

### Scene and character intelligence

- Scene Function Registry.
- Character Voice Pack.
- Branch Bible.
- Visual Bible.

### Evidence adapter contracts

- RAGFlow result -> `EvidenceItem`.
- LlamaIndex result -> `EvidenceItem`.
- Future parser result -> `NormalizedBlock` / `EvidenceItem`.

## 5. Adapter Rule

All external tools must pass through adapters:

```text
External backend
-> Adapter
-> EvidenceItem / NormalizedBlock
-> Context Pack
-> src/v1 task layer
```

Forbidden:

- Putting business rules inside RAGFlow, Dify, or Streamlit nodes.
- Letting an external backend directly decide Canon.
- Letting UI code perform continuity logic.
- Letting an LLM automatically canonize new material.

## 6. Adoption Process For Any New Tool

Every new tool must go through:

1. Evaluation plan.
2. 3-5 real project samples.
3. Result template.
4. Decision: Adopt / Optional / Reject.
5. Adapter contract.
6. Then code integration.

Forbidden:

- Installing a tool and immediately changing the mainline.
- Refactoring architecture because of one failed example.
- Connecting multiple tools of the same class at the same time.

## 7. Current Recommended Roadmap

Phase A:

- Finish RAGFlow backend evaluation plan.
- Manually test RAGFlow with 3-5 STUPID files.
- Decide whether RAGFlow becomes the external backend.

Phase B:

- If RAGFlow passes, build only `ragflow_evidence_adapter.py`.
- Do not move Canon logic into RAGFlow.

Phase C:

- Run terminal real capability tests:
  - Canon QA
  - Continuity Check
  - Story Brief
  - Art Prompt Brief

Phase D:

- Then reconnect stable terminal capability to Streamlit UI.

## 8. Explicit Non-goals

- Do not build a general RAG platform.
- Do not build a document parser from scratch.
- Do not build a vector database.
- Do not build an image generation backend.
- Do not migrate the project into Dify.
- Do not replace `src/v1` with RAGFlow.
- Do not add Haystack or LangGraph unless the current router is insufficient.
- Do not polish UI before terminal capability works.

## 9. Portfolio Positioning

This project demonstrates:

- AI-assisted narrative design workflow.
- Canon-aware governance.
- Evidence-grounded story development.
- Continuity checking.
- Integration with mature open-source AI infrastructure.
- Clear adapter-based architecture.
- Test-driven workflow development.

The portfolio value is not that the project reimplements every AI subsystem. The value is that it defines the narrative governance layer that makes external AI infrastructure useful and safe for game writing work.
