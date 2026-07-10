# RAGFlow Backend Evaluation Runbook

## Purpose

Evaluate whether RAGFlow can serve as an external ingestion and retrieval backend for the Canon-aware Narrative Intelligence Workflow.

This experiment is manual. Codex does not install RAGFlow, run Docker, upload files, or write an adapter in this step.

## Manual Setup Placeholder

Install and start RAGFlow manually by following the official RAGFlow documentation.

Do not commit RAGFlow database files, uploaded files, parser outputs, logs, or generated indexes into this repository.

## Suggested Manual Flow

1. Start RAGFlow locally.
2. Create dataset: `STUPID_RAGFLOW_EVAL`.
3. Upload 3-5 selected files.
4. Wait for parsing/indexing.
5. Ask the evaluation questions in `evaluation_cases.json`.
6. Export or copy retrieval evidence.
7. Fill `result_template.md`.
8. Decide whether to build an adapter.

## Safety

- Do not upload secret API keys into the repo.
- Do not commit RAGFlow data.
- Do not commit parsed sample outputs unless sanitized.
- RAGFlow result is evidence backend output only, not Canon authority.
- Canon / Draft / Deprecated / Inspiration status remains governed by `src/v1`.
