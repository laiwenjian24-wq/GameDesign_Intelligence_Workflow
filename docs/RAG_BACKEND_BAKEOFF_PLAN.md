# RAG Backend Bake-off for STUPID Narrative Workflow

## 0. Purpose

This document defines a technical evaluation plan for choosing whether STUPID Narrative Workflow should keep the current LlamaIndex path or adopt another open-source RAG backend.

This is a bake-off plan only.

Out of scope for this document:

- installing dependencies
- changing the current Workflow
- replacing Context Pack
- connecting a new framework into `main.py`
- changing `import_manifest.json`
- changing source knowledge-base documents
- adding answer generation

Current baseline:

- ingestion / metadata / manifest exist
- LlamaIndex BM25 retrieval works
- LLM-assisted retrieval works through `context-rag-llm`
- Context Pack remains the governance layer
- Canon / Draft / Deprecated / Inspiration separation is mandatory
- DeepSeek is used only for query planning and evidence selection, not final answers

## 1. Decision Criteria

The project should not choose a backend only by raw recall. The winning path must preserve the narrative governance model.

Primary criteria:

1. Evidence precision for narrative facts
2. Metadata and status preservation
3. Multitype document support
4. Reranking support
5. DeepSeek compatibility
6. Local/offline testability
7. Low migration cost
8. Portfolio readability

Hard constraints:

- `canon` can be used as factual evidence.
- `draft` is reference only.
- `deprecated` is warning / conflict-origin only.
- `inspiration` is not fact.
- Context Pack remains the final evidence product.
- LLM must not bypass evidence governance.

## 2. Candidate Summary

| Candidate | Positioning | Migration stance |
|---|---|---|
| RAGFlow | Full RAG product / platform with document parsing, chunking, retrieval, reranking, UI, services | Evaluate as productized RAG backend, not immediate library replacement |
| Haystack | Modular Python RAG pipeline framework | Strong candidate if we want explicit pipeline components and production structure |
| Docling + current Context Pack | Document conversion and structure extraction toolkit | Strong candidate for ingestion/chunk precision, not a full RAG replacement |
| Unstructured + current Context Pack | Document partitioning and element extraction toolkit | Strong candidate for heterogeneous files and ingestion normalization |
| LlamaIndex current baseline | Current implemented retrieval framework | Baseline to beat |
| LightRAG / GraphRAG | Lightweight graph or relation-aware retrieval layer | Future relationship/timeline layer, not main v0.4 retrieval migration |

## 3. Candidate Details

### 3.1 RAGFlow

Positioning:

- End-to-end RAG platform.
- Focuses on document ingestion, parsing, chunking, retrieval, reranking, knowledge-base management, and application workflows.
- More product/platform than lightweight Python library.

Why it may fit STUPID:

- Could quickly test stronger parsing + retrieval + reranking without building each component.
- Useful if the project later needs a visual knowledge-base management UI.
- Good for demonstrating a production-style RAG stack in a portfolio.

Risks:

- Heavier operational footprint than the current local Python workflow.
- May introduce database, service, Docker, and web UI dependencies.
- Harder to preserve the exact current Context Pack structure unless wrapped carefully.
- Could shift the project from a clear code-first workflow into a platform integration.

Dependency / install path for experiment:

```powershell
# Do not run during planning.
# Expected approach: clone RAGFlow repo and run its documented Docker setup.
git clone https://github.com/infiniflow/ragflow
```

Multitype documents:

- Expected to support common document ingestion scenarios.
- Must be verified with STUPID Markdown, TXT, PDF, image metadata, and generated markdown excerpts.

Metadata/status preservation:

- Needs explicit experiment.
- Critical question: can `status=canon/draft/deprecated/inspiration` survive ingestion, retrieval, and reranking as filterable metadata?

Reranker support:

- Likely a core platform strength.
- Must verify local or API-based reranker options and whether DeepSeek can be used.

DeepSeek suitability:

- Potentially suitable if OpenAI-compatible API configuration is supported.
- Must verify JSON-only planning and evidence-selection calls separately.

Portfolio suitability:

- Strong if presented as an evaluated backend option.
- Risky if it hides too much of the custom narrative governance logic.

Minimum experiment:

1. Create isolated RAGFlow sandbox.
2. Import only 6-8 representative STUPID documents.
3. Attach status metadata if supported.
4. Query the unified test set.
5. Export retrieved evidence with source metadata.
6. Compare against LlamaIndex Context Pack.

Verdict to test:

- Best as a platform comparison.
- Do not migrate unless it can preserve Context Pack governance cleanly.

### 3.2 Haystack

Positioning:

- Python framework for custom RAG pipelines.
- Emphasizes explicit components: converters, embedders, retrievers, rankers, prompt builders, generators, routers.
- Better fit for code-first engineering than full RAG platforms.

Why it may fit STUPID:

- Pipeline structure maps well to current Workflow stages.
- Strong explicit routing could preserve Canon / Draft / Deprecated / Inspiration separation.
- Good for a portfolio because pipelines are visible, testable, and explainable.

Risks:

- Migration cost is non-trivial.
- Requires rebuilding ingestion/retrieval adapters.
- Some features may require extra integrations for vector stores, rankers, and document converters.
- The current LlamaIndex path already works; Haystack must prove better evidence precision or maintainability.

Dependency / install path for experiment:

```powershell
# Do not run during planning.
E:\Desktop\python310\python.exe -m pip install haystack-ai
```

Multitype documents:

- Supports document converters and can integrate external parsers.
- Must test Markdown heading structure, PDF conversion, and images separately.

Metadata/status preservation:

- Strong candidate.
- Haystack Document metadata can likely carry `source_file`, `status`, `asset_type`, `tags`, `heading`, `section_title`.
- Must verify metadata survives retrievers and rankers.

Reranker support:

- Strong candidate.
- Haystack supports ranker components and can route retrieved docs through rerankers.

DeepSeek suitability:

- Suitable if using a custom OpenAI-compatible generator/client or a lightweight custom component.
- For this project, DeepSeek should remain query planner / selector only unless later approved.

Portfolio suitability:

- Strong.
- A pipeline diagram can show exactly how governance is enforced.

Minimum experiment:

1. Build a sandbox `haystack_bakeoff.py`.
2. Convert current node JSON or manifest documents into Haystack Documents.
3. Preserve all governance metadata.
4. Implement BM25 retrieval first.
5. Add optional embedding/ranker only after BM25 baseline.
6. Export candidate evidence into current Context Pack shape.

Verdict to test:

- Strongest candidate if the project wants a production-grade Python pipeline framework.
- Must outperform LlamaIndex on evidence precision without increasing complexity too much.

### 3.3 Docling + Current Context Pack

Positioning:

- Document conversion and structure extraction toolkit.
- Not a full RAG backend by itself.
- Best evaluated as an ingestion/chunking upgrade.

Why it may fit STUPID:

- Current problem is not only retrieval; chunk precision matters.
- Docling may improve structured parsing of PDF/table-rich documents.
- It can feed better sections into the current Context Pack without replacing retrieval governance.

Risks:

- Does not solve retrieval/reranking alone.
- Adds a conversion layer and possibly model/layout dependencies.
- If current assets are mostly Markdown, benefit may be limited.

Dependency / install path for experiment:

```powershell
# Do not run during planning.
E:\Desktop\python310\python.exe -m pip install docling
```

Multitype documents:

- Strong candidate for PDFs and document conversion.
- Must verify Markdown, PDF, TXT, and any image/visual-reference workflows.

Metadata/status preservation:

- Should be possible because metadata can be added after conversion.
- Must ensure section/table metadata can be mapped into existing node metadata.

Reranker support:

- None by itself.
- Pair with current LlamaIndex, Haystack, or custom selector.

DeepSeek suitability:

- Indirect.
- Better document structure should improve DeepSeek evidence selection.

Portfolio suitability:

- Strong if framed as "document intelligence layer feeding a narrative evidence pipeline."
- Less impressive as a standalone RAG backend.

Minimum experiment:

1. Pick 3 document types: Markdown, PDF, visual-reference markdown/table.
2. Convert with Docling.
3. Compare section/table structure against current Markdown section chunking.
4. Feed converted sections into current Context Pack path.
5. Run unified test questions.

Verdict to test:

- Best candidate for improving ingestion precision while preserving current architecture.
- Likely additive rather than a replacement.

### 3.4 Unstructured + Current Context Pack

Positioning:

- Document partitioning / extraction toolkit.
- Converts files into typed elements such as titles, narrative text, tables, images, etc.
- Not a complete RAG framework by itself.

Why it may fit STUPID:

- Useful if the knowledge base expands beyond Markdown.
- Element-level parsing could improve heading-aware and table-aware chunking.
- Works well as an upstream normalization layer before Context Pack.

Risks:

- Adds dependency weight.
- Quality varies by file type and installed extras.
- May require careful post-processing to maintain useful narrative section boundaries.

Dependency / install path for experiment:

```powershell
# Do not run during planning.
E:\Desktop\python310\python.exe -m pip install unstructured
```

Multitype documents:

- Strong candidate.
- Must test required extras for PDF/images separately.

Metadata/status preservation:

- Should be possible by attaching manifest metadata to each extracted element.
- Must verify table/heading element metadata remains usable.

Reranker support:

- None by itself.
- Pair with LlamaIndex/Haystack/current selector.

DeepSeek suitability:

- Indirect.
- Better element chunks can make DeepSeek selector less likely to see noisy text.

Portfolio suitability:

- Good if positioned as a robust ingestion option.
- Less compelling than Haystack if the goal is full RAG architecture.

Minimum experiment:

1. Partition 6 representative assets.
2. Map elements to node schema.
3. Preserve manifest status metadata.
4. Feed elements into existing LlamaIndex BM25 path.
5. Compare evidence precision against current section-aware chunks.

Verdict to test:

- Good ingestion candidate.
- Not a standalone replacement for current RAG path.

### 3.5 LlamaIndex Current Baseline

Positioning:

- Current implemented baseline.
- LlamaIndex provides node parsing, BM25 retrieval, optional vector retrieval, query fusion, and extensibility.
- The project already wraps it with Context Pack governance.

Why it fits STUPID:

- Already integrated.
- Works with current `context-rag-llm`.
- Preserves custom metadata/status.
- Easy to keep as code-first portfolio implementation.
- Current failure mode is understandable and fixable: query planning and evidence precision.

Risks:

- Out-of-the-box BM25 has weak Chinese short-question recall.
- Requires custom glue for governance.
- Can accumulate local wrappers if not controlled.
- Vector/reranker setup still needs careful dependency management.

Dependency / install path:

```powershell
E:\Desktop\python310\python.exe -m pip install -r requirements.txt
```

Multitype documents:

- Good with custom loaders/converters.
- Needs Docling/Unstructured or custom loaders for stronger PDF/image/table handling.

Metadata/status preservation:

- Proven in current implementation.

Reranker support:

- Available through LlamaIndex integrations, but not yet enabled in this project.

DeepSeek suitability:

- Proven for query rewrite / evidence selection through current provider.
- Answer generation remains intentionally out of scope.

Portfolio suitability:

- Strong because the custom governance layer is visible and testable.

Minimum experiment:

1. Treat current branch as baseline.
2. Freeze output from `context-rag-llm` for the unified questions.
3. Measure evidence precision and status separation.
4. Add reranker only as a controlled sub-experiment.

Verdict to test:

- Default incumbent.
- Other candidates must beat it on precision or reduce complexity.

### 3.6 LightRAG / GraphRAG

Positioning:

- Relationship-aware or graph-enhanced retrieval.
- Better suited to connections: character relationships, organization membership, timeline causality, branch state.

Why it may fit STUPID later:

- STUPID has heavy relationship/state questions:
  - Rain / Snow
  - Mouse / Rin trust
  - Second Foundation
  - branch outcomes
  - Judgment Day causal structure

Risks:

- Too early as a main retrieval backend.
- Graph extraction can invent relations if not carefully grounded.
- Needs a canon-governed entity/relation schema first.

Dependency / install path:

```powershell
# Do not run during planning.
# Evaluate only after RAG backend bake-off.
```

Multitype documents:

- Depends on implementation.

Metadata/status preservation:

- Must be mandatory.
- Graph nodes and edges must retain source status and citation.

Reranker support:

- Not the main value.
- Graph traversal is the value.

DeepSeek suitability:

- Useful for extraction, but high hallucination risk.
- Should require strict citation-backed relation extraction.

Portfolio suitability:

- Strong future layer if framed as "Narrative State Graph."
- Not appropriate for immediate backend migration.

Minimum experiment:

1. Do not run in current bake-off.
2. Later extract 10 canon relationship facts only.
3. Require source citation per edge.
4. Compare relationship/timeline questions against Context Pack.

Verdict to test:

- Future relationship layer, not v0.4 backend replacement.

## 4. Unified Test Question Set

The same questions must be run for every candidate. Each output must be converted into current Context Pack sections.

### Character Identity / State

1. `Rin是什么身份？`
2. `Mouse过去是什么身份？`
3. `Mouse的左眼是什么状态？`
4. `Snow是什么实验对象？`
5. `Rain和Second Foundation是什么关系？`

### World / Concept

6. `Judgment Day是什么事件？`
7. `SDFT是什么？`
8. `Brain Ladder是什么？`

### Branch / Continuity

9. `Branch B里Rin哪里受伤？`
10. `分支A和分支B在风筝任务中有什么差异？`
11. `Rin右腿受伤这个说法可靠吗？`

### Relationship / Narrative Reasoning

12. `Mouse为什么会改变对仿生人的看法？`
13. `Rain和Snow的关系是什么？`
14. `Larry和Second Foundation有什么关系？`

### Negative / Missing Evidence

15. `Rin是Nexus-6吗？`
16. `Mouse是否拥有火星基地？`
17. `Julie是不是Second Foundation成员？`

## 5. Expected Evidence Rules

Every backend must produce evidence that can be mapped into:

- `canon_context`
- `draft_reference`
- `deprecated_warnings`
- `inspiration_context`
- `missing_evidence`
- `restrictions`
- `evidence_sources`

Evidence item minimum fields:

```json
{
  "source_file": "...",
  "status": "canon",
  "asset_type": "...",
  "heading": "...",
  "section_title": "...",
  "excerpt": "...",
  "score": 0.0,
  "retrieval_mode": "...",
  "reason_used": "..."
}
```

Disqualifying failures:

- Draft evidence enters `canon_context`.
- Deprecated evidence is treated as current truth.
- Inspiration source is used as fact.
- Source file is missing.
- Status metadata is missing.
- Answer is produced without evidence.

## 6. Unified Evaluation Table

Use this table for each backend and each test question.

| Metric | Score 0 | Score 1 | Score 2 | Score 3 |
|---|---|---|---|---|
| Canon recall | No relevant canon | Weak/indirect canon | Relevant canon but noisy | Direct canon section |
| Evidence precision | Wrong excerpt | Broad unrelated chunk | Relevant but verbose | Direct sentence/table row |
| Status separation | Broken | Partially preserved | Preserved with warnings | Fully preserved |
| Metadata retention | Missing key fields | Source only | Source + status | Full manifest metadata |
| Reranking quality | None/worse | Minor improvement | Good ordering | Best evidence first |
| DeepSeek fit | Not supported | Custom difficult | Works with wrapper | Clean structured integration |
| Local testability | Not testable | Heavy/manual | Scriptable | Offline/unit-testable |
| Portfolio clarity | Opaque | Hard to explain | Explainable | Strong architecture story |
| Migration cost | High rewrite | Medium rewrite | Low adapter | Drop-in/additive |

Pass threshold for a serious candidate:

- Average score >= 2.2
- Status separation score must be 3
- Metadata retention score must be >= 2
- At least 12/17 questions must retrieve relevant canon when canon exists

## 7. Bake-off Procedure

### Phase 1: Baseline Freeze

1. Run current LlamaIndex `context-rag-llm` for all test questions.
2. Save output manually under a non-committed `outputs/rag_bakeoff/` folder.
3. Score current baseline.

### Phase 2: Ingestion-only Candidates

Evaluate:

- Docling + current Context Pack
- Unstructured + current Context Pack

Procedure:

1. Convert representative files.
2. Map elements into current node schema.
3. Preserve manifest metadata.
4. Feed into current LlamaIndex retrieval path.
5. Compare evidence precision.

Decision:

- If either improves section precision without breaking metadata, consider it as ingestion upgrade.
- Do not replace retrieval just because conversion is better.

### Phase 3: Pipeline Candidate

Evaluate:

- Haystack

Procedure:

1. Build one isolated pipeline.
2. Use same document subset.
3. Preserve status metadata.
4. Run BM25 first, then optional ranker.
5. Export Context Pack-compatible output.

Decision:

- Consider migration only if Haystack provides better precision and a cleaner pipeline than current LlamaIndex wrappers.

### Phase 4: Platform Candidate

Evaluate:

- RAGFlow

Procedure:

1. Run isolated service.
2. Import same document subset.
3. Test metadata/status preservation.
4. Export retrieval results.
5. Compare against Context Pack requirements.

Decision:

- Treat as optional platform benchmark.
- Do not migrate unless Context Pack governance remains first-class.

### Phase 5: Future Graph Layer

Evaluate later:

- LightRAG / GraphRAG

Procedure:

1. Define canon relationship schema first.
2. Extract only cited canon relations.
3. Do not mix graph output into factual answer without Context Pack.

Decision:

- Future layer for relationship/timeline/branch reasoning.
- Not a main backend migration in this bake-off.

## 8. Recommendation Before Experiments

Do not replace the current LlamaIndex path yet.

Recommended order:

1. Keep LlamaIndex as baseline.
2. Evaluate Docling and Unstructured as ingestion/chunking upgrades.
3. Evaluate Haystack as a code-first pipeline alternative.
4. Evaluate RAGFlow only as a heavier platform benchmark.
5. Defer LightRAG / GraphRAG until a canon relationship schema exists.

Most likely useful outcomes:

- Short term: Docling or Unstructured improves chunk precision.
- Medium term: Haystack may offer cleaner production pipeline architecture.
- Long term: Graph layer helps relationship/timeline questions.

## 9. Source Links For Follow-up

These are starting points for later verification, not installed dependencies.

- RAGFlow: https://github.com/infiniflow/ragflow
- Haystack docs: https://docs.haystack.deepset.ai/
- Haystack GitHub: https://github.com/deepset-ai/haystack
- Docling GitHub: https://github.com/docling-project/docling
- Docling technical report: https://arxiv.org/abs/2408.09869
- Unstructured docs: https://docs.unstructured.io/
- Unstructured GitHub: https://github.com/Unstructured-IO/unstructured
- LlamaIndex docs: https://docs.llamaindex.ai/
- LightRAG GitHub: https://github.com/HKUDS/LightRAG
- Microsoft GraphRAG: https://github.com/microsoft/graphrag

