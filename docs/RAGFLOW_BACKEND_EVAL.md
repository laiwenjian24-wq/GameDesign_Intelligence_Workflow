# RAGFlow Backend Evaluation for Canon-aware Narrative Workflow

## 1. Purpose

This document evaluates whether RAGFlow / DeepDoc is suitable as an external ingestion and retrieval backend for the Canon-aware Narrative Intelligence Workflow.

The evaluation focuses on whether RAGFlow can help with:

- Multi-format project material ingestion.
- PDF / image OCR.
- Layout-aware parsing.
- Knowledge base construction.
- Evidence retrieval.

The project must still preserve its own Canon-aware narrative workflow. RAGFlow may provide infrastructure, but it must not become Canon authority.

## 2. Why Not Dify as Core

Dify is useful for generic RAG chatbots and workflow apps. It can be valuable later as a comparison tool or demo shell.

This project's core is not a generic chatbot. The core is Canon-aware narrative governance:

- Canon / Draft / Deprecated / Inspiration status separation.
- Source policy.
- Continuity checking.
- Branch-state reasoning.
- Scene and character constraints.
- Story Brief and Art Prompt Brief rules.

Therefore, the core workflow should remain in `src/v1`. Dify should not become the source of Canon logic or continuity policy.

## 3. Why Evaluate RAGFlow / DeepDoc

RAGFlow / DeepDoc is closer to the current infrastructure gap than Dify because the project needs better ingestion and retrieval, especially for:

- Markdown / PDF / DOCX / PPTX / image ingestion.
- OCR.
- Table, figure, and layout-aware parsing.
- Knowledge base management.
- Retrieval API / SDK possibility.

If it works well, RAGFlow can become an external backend behind a v1 evidence adapter.

## 4. Target Architecture

Target flow:

```text
Documents
-> RAGFlow / DeepDoc
-> RAGFlow dataset / knowledge base
-> RAGFlow retrieval API
-> v1 evidence adapter
-> Canon-aware narrative layer
-> Daily Narrative Assistant
-> CLI / Streamlit
```

RAGFlow is a retrieval backend, not Canon authority.

The Canon-aware layer remains in `src/v1`.

## 5. What RAGFlow Must Prove

RAGFlow must prove:

1. It can ingest a Markdown Canon file.
2. It can ingest PDF.
3. It can ingest DOCX or PPTX.
4. It can ingest an image containing text.
5. It can retrieve source-grounded evidence.
6. It can preserve useful metadata such as file name, page number, and chunk text.
7. It can be queried through API or SDK.
8. It can integrate with external status metadata from `import_manifest`.
9. It does not force the project to abandon the `src/v1` workflow.

## 6. Evaluation Dataset

Do not copy original project files into this document.

Select:

- 1 Canon Markdown file.
- 1 PDF file.
- 1 DOCX or PPTX file.
- 1 image containing text.
- 1 Deprecated / old draft file.

For each file, record:

- File path.
- File type.
- Expected status.
- Expected key evidence.

## 7. Evaluation Questions

Use these questions:

1. `Rin是什么身份？`
2. `Branch B中Rin哪条腿受伤？`
3. `Mouse在Branch B的伤势是什么？`
4. `Mombasa安全屋场景功能是什么？`
5. `右腿受伤设定能不能作为当前 Canon？`
6. `Branch B 互相包扎 CG prompt 需要哪些 continuity constraints？`

## 8. Scoring Criteria

Score each item:

- 0 = failed
- 1 = weak
- 2 = usable
- 3 = strong

| Criterion | Score | Notes |
|---|---:|---|
| installation difficulty |  |  |
| Docker/resource cost |  |  |
| Markdown parsing quality |  |  |
| PDF parsing quality |  |  |
| image OCR quality |  |  |
| DOCX/PPTX parsing quality |  |  |
| table/figure handling |  |  |
| source citation quality |  |  |
| page number metadata |  |  |
| API/SDK usability |  |  |
| metadata/status integration |  |  |
| retrieval quality |  |  |
| integration cost |  |  |
| platform lock-in risk |  |  |
| portfolio value |  |  |

## 9. Decision Rules

Use RAGFlow as an external backend if:

- It can ingest at least Markdown + PDF + image.
- It returns useful source metadata.
- It supports API / SDK retrieval.
- It does not require moving Canon logic into RAGFlow.
- It can be connected through an evidence adapter.

Do not use RAGFlow as backend if:

- Setup is too heavy for a personal demo.
- API retrieval is difficult.
- Metadata is poor.
- It cannot handle status separation through external mapping.
- It forces platform lock-in.

## 10. Non-goals

- Not migrating the project into RAGFlow.
- Not using RAGFlow as Canon authority.
- Not replacing `src/v1`.
- Not replacing tests.
- Not replacing Streamlit.
- Not integrating Dify.
- Not building production deployment.
