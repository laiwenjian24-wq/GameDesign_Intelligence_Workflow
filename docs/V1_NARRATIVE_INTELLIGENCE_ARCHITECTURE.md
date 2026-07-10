# V1 Narrative Intelligence Workflow Architecture

## 1. Product Positioning

GameDesign_Intelligence_Workflow v1 is not a generic RAG app. It is a Canon-aware Narrative Intelligence Workflow / Workbench for narrative game development.

The product goal is to help designers manage, query, validate, and later produce story material while preserving narrative authority and source grounding.

Core value:

- Multi-format narrative source ingestion.
- Canon / Draft / Deprecated / Inspiration governance.
- Stable answers to project-setting questions.
- Conflict checks for newly imported or newly written content.
- Future support for story continuation and art prompt generation.
- Natural-language entry point, so users do not need to memorize fixed command formats.

RAG is infrastructure. The product is the narrative workflow around evidence, canon status, continuity, branch state, character voice, and production decisions.

## 2. Lessons from v0.4

v0.4 has completed the experimental RAG layer:

- Manifest / metadata workflow.
- Canon / Draft / Deprecated / Inspiration separation.
- LlamaIndex BM25 retrieval.
- LLM-assisted query rewrite.
- Evidence selection.
- DeepSeek provider.
- Full-context baseline.
- `ask-full` / `ask-rag` comparison.

The main lesson is that chunk-based RAG is useful but insufficient as the project identity.

What v0.4 can do:

- Answer many single-entity factual questions.
- Preserve source metadata and status labels.
- Produce inspectable evidence packs.
- Compare retrieval-based answers against full-context answers.

What v0.4 exposed:

- Chunk-based RAG is weaker on relationship questions.
- Multi-hop evidence is unstable.
- Alias handling is incomplete.
- Cross-document relationship understanding is limited.
- Evidence selection can miss the best support even when the corpus contains it.
- A single failed example should not trigger hardcoded patches.

The next step is not more one-off retrieval tuning. The project should become a v1 Narrative Intelligence Workflow where retrieval, graph structure, evidence governance, continuity checking, and future generation tools are coordinated under a clear product architecture.

## 3. Target Capabilities

MVP:

1. `ingest`
2. `build-index`
3. `chat ask`
4. `check-continuity`

Phase 2:

5. Story continuation.
6. Art prompt generation.
7. Streamlit demo / UI.

Long-term:

8. Asset analysis.
9. GraphRAG relationship QA.
10. Ren'Py / Ink / Yarn export support.

## 4. Natural Language Task Interface

The final user-facing entry point should be:

```powershell
main.py chat "自然语言需求"
```

Users should not need to know whether their request maps internally to `ask`, `ask-relation`, `check-continuity`, `continue-story`, `art-prompt`, or another tool.

Example user requests:

- `Rain和Second Foundation是什么关系？`
- `Rin右腿受伤这个设定能用吗？`
- `帮我续写Mombasa安全屋里的下一场戏。`
- `给我生成Branch B互相包扎场景的CG prompt。`
- `我刚导入的PDF里有哪些内容可能和Canon冲突？`

Internally, an LLM Request Planner should convert the natural-language request into a structured task.

Planner output fields:

- `task_type`
- `user_intent`
- `entities`
- `aliases`
- `constraints`
- `branch_scope`
- `requested_output`
- `required_evidence`
- `confidence`
- `clarification_needed`
- `clarification_question`

Minimum `task_type` values:

- `canon_qa`
- `relationship_qa`
- `continuity_check`
- `story_continuation`
- `art_prompt_generation`
- `document_ingestion`
- `asset_analysis`
- `benchmark_eval`
- `unknown`

If confidence is low or the branch scope materially affects the answer, the planner should ask for clarification instead of guessing.

## 5. Layered Architecture

### 1. Project Source Layer

Responsibility:

- Store original project material and source metadata.
- Preserve document provenance and authorial status.

Input:

- Markdown, TXT, PDF, image references, design notes, exported scripts, asset descriptions.

Output:

- Source files plus manifest records with status and asset metadata.

Suggested open-source tools:

- Filesystem storage.
- Git for version history.

Custom project logic:

- `Canon / Draft / Deprecated / Inspiration` status model.
- Manifest validation.
- Source provenance rules.
- Import review queue.

### 2. Document Understanding Layer

Responsibility:

- Convert heterogeneous documents into normalized, structured narrative material.
- Preserve headings, tables, sections, images, and source locations where possible.

Input:

- Raw project source files.

Output:

- Normalized Markdown / JSON.
- Extracted sections, tables, claims, visual references, and metadata.

Suggested open-source tools:

- Docling as primary parser.
- PaddleOCR for OCR fallback.
- Marker / Unstructured as bakeoff candidates.

Custom project logic:

- Narrative-aware section labeling.
- Manifest metadata attachment.
- Status preservation.
- Claim extraction candidates.

### 3. Knowledge Index Layer

Responsibility:

- Build indexes that can support factual QA, relationship QA, continuity checks, and future generation.

Input:

- Normalized documents and extracted metadata.

Output:

- Chunk index.
- Vector index.
- Optional graph index.
- Evidence-source registry.

Suggested open-source tools:

- LlamaIndex hybrid retrieval.
- BM25.
- Vector retrieval.
- Optional reranker.
- LlamaIndex Property Graph for first graph experiment.

Custom project logic:

- Context Pack schema.
- Canon-safe filtering.
- Source-cited graph edge schema.
- Branch-aware metadata.

### 4. Retrieval and Reasoning Layer

Responsibility:

- Retrieve relevant evidence.
- Separate current fact, reference, warning, inspiration, and missing evidence.
- Reason only within the permissions of source status.

Input:

- Structured task plan.
- Indexes.
- User constraints.

Output:

- Evidence pack.
- Missing evidence report.
- Canon-safe reasoning context.

Suggested open-source tools:

- LlamaIndex retrievers.
- BM25 + vector hybrid retrieval.
- Reranker optional.
- DeepSeek or OpenAI-compatible LLM provider for planning and evidence selection.

Custom project logic:

- Draft cannot override Canon.
- Deprecated can only explain historical conflict.
- Inspiration cannot be used as fact.
- Evidence must carry source, status, and citation metadata.

### 5. Narrative Task Layer

Responsibility:

- Execute narrative workflows on top of evidence and project rules.

Input:

- Task plan.
- Evidence pack.
- Narrative Bible.
- Scene Function Registry.
- Character Voice Pack.

Output:

- Canon QA answer.
- Relationship answer.
- Continuity report.
- Scene draft.
- Art prompt.
- Review recommendation.

Suggested open-source tools:

- Haystack for explicit workflow orchestration.
- LangGraph later for stateful multi-step agents.

Custom project logic:

- Canon-aware answer formatter.
- Continuity conflict taxonomy.
- Scene function checks.
- Character voice constraints.
- Branch-state validation.

### 6. Evaluation and Interface Layer

Responsibility:

- Provide user and developer entry points.
- Measure behavior with narrative-specific benchmarks.
- Preserve reproducibility.

Input:

- CLI requests.
- Benchmark questions.
- Evaluation fixtures.

Output:

- User-facing answers.
- Debug traces.
- Benchmark reports.
- Regression results.

Suggested open-source tools:

- RAGChecker.
- DeepEval.
- Langfuse / Phoenix later.
- Streamlit later.

Custom project logic:

- Narrative Intelligence Benchmark.
- Fixed fake provider tests.
- Canon governance regression cases.
- Human-readable evidence comparison.

## 6. Open-source Stack

Document parsing:

- Docling primary.
- PaddleOCR for OCR fallback.
- Marker / Unstructured as bakeoff candidates.

RAG:

- LlamaIndex hybrid retrieval.
- BM25 + vector retrieval.
- Reranker optional.

GraphRAG:

- LlamaIndex Property Graph as first experiment.
- LightRAG as bakeoff candidate.
- Microsoft GraphRAG / Graphiti / RetriCo as research candidates.

Workflow orchestration:

- Haystack first.
- LangGraph later for stateful agents.

LLM:

- Fake provider for tests.
- DeepSeek provider for real runs.
- OpenAI-compatible provider interface.

Evaluation:

- RAGChecker.
- DeepEval.
- Langfuse / Phoenix later.

Image backend:

- Prompt generation first.
- ComfyUI / InvokeAI optional in Phase 2+.

Narrative export:

- Ren'Py first.
- Ink / Yarn Spinner optional later.

## 7. Narrative Bible Layer

The Narrative Bible Layer is the structured source of constraints for narrative production. These bibles are not ordinary documents. They are governed, queryable, and reviewable constraint sources used by QA, continuity checking, story continuation, and art prompt generation.

Core bibles:

- Character Bible: identities, relationships, states, wounds, motives, boundaries, voice constraints.
- World Bible: locations, factions, technology, historical events, rules of the setting.
- Branch Bible: branch-specific state, player knowledge, divergent outcomes, allowed continuity.
- Scene Bible: scene purpose, emotional function, required beats, preserved consequences.
- Visual Bible: character appearance, costumes, locations, palette, framing constraints.
- Prompt Bible: reusable production prompt rules, negative prompts, style constraints, output formats.

Each bible entry should retain source evidence and canon status. A bible entry is only authoritative when backed by reviewed Canon.

## 8. Scene Function Registry

Every important scene should record its dramatic function, branch state, and production constraints.

Required fields:

- `scene_id`
- `branch`
- `scene_function`
- `emotional_purpose`
- `player_knowledge_state`
- `characters`
- `location`
- `must_preserve`
- `must_avoid`
- `source_files`

Example:

Branch B's mutual bandaging scene should not be treated as generic romance. Its function is reciprocal care / restrained trust. The scene should preserve mutual vulnerability, limited verbal expression, and the branch-specific emotional state. It should avoid sudden confession, exaggerated intimacy, or behavior that collapses the established restraint.

This registry lets the system evaluate whether a continuation or art prompt preserves the scene's design role instead of only checking factual consistency.

## 9. Character Voice Pack

Character-accurate continuation cannot rely only on factual RAG. It also needs voice, behavior, and emotional constraints.

Each character should record:

- Speech style.
- Behavior boundaries.
- Emotional range.
- Forbidden moves.
- Example lines.
- Source evidence.

The Character Voice Pack should answer questions such as:

- What would this character say directly?
- What would they avoid saying?
- How do they show care, anger, fear, loyalty, or distrust?
- What behavior would break the audience's sense of the character?

Voice constraints must be source-grounded. If evidence is missing, the system should report uncertainty instead of inventing a voice rule.

## 10. Canonization Workflow

Newly imported material must not automatically become Canon.

Workflow:

```text
Imported
-> Parsed
-> Indexed
-> Candidate Claims Extracted
-> Human Review
-> Canon / Draft / Deprecated / Inspiration
```

Governance rules:

- Draft cannot override Canon.
- Deprecated can only be used as historical conflict source.
- Inspiration cannot be used as fact.
- LLM cannot automatically decide canon.

The LLM may assist by extracting candidate claims, identifying conflicts, summarizing differences, and preparing review notes. The final status decision remains human-controlled.

## 11. Continuity Check Taxonomy

Continuity checking must be graded, not binary.

Conflict types:

- Factual conflict.
- Branch-state conflict.
- Character-behavior conflict.
- Tone/theme conflict.
- Deprecated contamination.
- Missing evidence.

Continuity output should include:

- `conflict_type`
- `severity`
- `new_claim`
- `canon_claim`
- `source_evidence`
- `suggested_fix`

Severity should reflect production impact. A minor wording mismatch is different from a branch-state contradiction or a deprecated claim being reintroduced as current Canon.

## 12. Main Workflows

### A. ingest

Flow:

```text
multi-format documents
-> normalized markdown/json
-> metadata attachment
-> review queue
```

Purpose:

- Bring project material into a consistent, source-tracked form without automatically changing canon status.

### B. build-index

Flow:

```text
normalized docs
-> chunk index
-> vector index
-> optional graph index
```

Purpose:

- Build the retrieval infrastructure used by QA, continuity checks, and later generation tools.

### C. chat ask

Flow:

```text
natural language
-> planner
-> task router
-> evidence pack
-> answer with citations
```

Purpose:

- Let users ask project-setting questions without knowing internal command names.

### D. check-continuity

Flow:

```text
new content
-> claim extraction
-> canon retrieval
-> contradiction report
```

Purpose:

- Identify conflicts before new material is promoted or used in production.

### E. story continuation

Flow:

```text
scene request
-> scene state + character voice + branch context
-> scene draft
```

Purpose:

- Produce draft continuation that respects scene function, character voice, branch state, and Canon constraints.

### F. art prompt generation

Flow:

```text
visual request
-> art bible + scene state + character constraints
-> production prompt
```

Purpose:

- Generate art prompts that preserve canon appearance, scene function, branch state, and production style constraints.

## 13. CLI Proposal

Primary user-facing command:

- `main.py chat "自然语言需求"`

Developer / debug / evaluation commands:

- `main.py ingest`
- `main.py build-index`
- `main.py ask`
- `main.py ask-relation`
- `main.py check-continuity`
- `main.py continue-story`
- `main.py art-prompt`
- `main.py context-full`
- `main.py context-rag-llm`
- `main.py eval-benchmark`

These are future command proposals. They are not implemented by this document step.

## 14. MVP Scope

v1 MVP includes only:

1. `ingest`
2. `build-index`
3. `chat ask`
4. `check-continuity`

Explicitly out of MVP:

- Full image generation.
- Streamlit UI.
- Automatic canonization.
- Direct RAGFlow migration.
- Full GraphRAG production backend.
- Ren'Py export.
- Story continuation production mode.
- Art prompt production mode.

Phase 2 should preserve story continuation and art prompt generation as planned extensions, but not allow them to distract from the core governance workflow.

## 15. GraphRAG Strategy

GraphRAG should not enter the MVP mainline, but it should remain a parallel experiment.

Reasons:

- Relationship QA needs entity / relation retrieval.
- Chunk RAG is unstable for relationship-heavy questions.
- Timeline, faction, branch-state, and causality questions benefit from graph structure.
- Graph extraction can hallucinate relations if not strictly governed.

The project should first define a source-cited canon edge schema.

Minimum graph edge fields:

- `subject`
- `relation`
- `object`
- `branch_scope`
- `status`
- `source_file`
- `source_excerpt`
- `confidence`
- `review_state`

Recommended experiment order:

1. LlamaIndex Property Graph first.
2. LightRAG bakeoff second.
3. Graphiti for temporal / provenance research.

Graph output must not bypass Context Pack governance. A graph relation is only usable as factual evidence when it is source-cited and Canon-reviewed.

## 16. Evaluation Benchmark

The project should define a Narrative Intelligence Benchmark. Evaluation is a first-class architecture component, not a late test add-on.

Benchmark question types:

- Canon fact QA.
- Relationship QA.
- Branch-state QA.
- Continuity conflict check.
- Deprecated contamination.
- Missing evidence.
- Character behavior check.
- Tone/theme check.
- Art prompt constraint check.

Each benchmark case should record:

- Input request.
- Expected task type.
- Required evidence.
- Forbidden evidence.
- Expected status handling.
- Expected answer behavior.
- Failure modes to detect.

The benchmark should measure narrative governance, not only retrieval recall.

## 17. Migration Plan

Phase 0:

- Keep v0.4 as legacy baseline.

Phase 1:

- Create v1 architecture and handoff docs.

Phase 2:

- Docling ingestion experiment.

Phase 3:

- Normalized document store.

Phase 4:

- Natural-language planner + chat routing skeleton.

Phase 5:

- Canon-aware ask pipeline.

Phase 6:

- Continuity checker v1.

Phase 7:

- GraphRAG relationship experiment.

Phase 8:

- Story continuation and art prompt tools.

Phase 9:

- Streamlit demo.

## 18. Portfolio Positioning

Resume / portfolio description:

A canon-aware AI narrative workflow for game development: multi-format ingestion, hybrid RAG / GraphRAG knowledge base, natural-language task routing, continuity checking, source-grounded QA, and future story/art generation support.

This positioning is stronger than presenting the project as a generic RAG demo because it highlights the actual product problem: helping narrative game teams preserve continuity, canon authority, branch state, character voice, and production-ready evidence.

## 19. Non-goals

This project is not:

- A generic RAG platform.
- An automatic game writer.
- A model training project.
- An image generation platform.
- A document management system.
- A direct fork of RAGFlow / GraphRAG.

The v1 architecture should stay focused on a specific workflow: helping game designers import, govern, query, validate, and later produce narrative material with canon-aware evidence control.
