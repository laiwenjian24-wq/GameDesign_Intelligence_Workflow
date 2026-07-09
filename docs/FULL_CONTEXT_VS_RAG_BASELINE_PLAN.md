# Full-context vs RAG Baseline Evaluation Plan

## 1. Purpose

This evaluation establishes a controlled baseline for deciding when STUPID Narrative Workflow should use direct full-context LLM reading, and when it should rely on the current RAG + Context Pack workflow.

The current RAG workflow has already implemented:

- Canon / Draft / Deprecated / Inspiration separation
- LlamaIndex BM25 retrieval
- LLM-assisted query rewrite
- DeepSeek provider
- Evidence selection
- Context Pack output

Manual testing shows that the workflow is useful, but not yet universally reliable:

- LLM-assisted retrieval can still select imperfect evidence.
- Plain BM25 retrieval is unstable for short Chinese questions.
- For a small narrative corpus, directly giving the LLM all relevant documents may produce better reasoning than retrieval.

This comparison is needed so future architecture decisions are based on measured behavior rather than intuition.

## 2. Compared Modes

### Mode A: Full-context baseline

Definition:

- Read source documents from `import_manifest.json`.
- Group and concatenate material by `status`:
  - Canon
  - Draft
  - Deprecated
  - Inspiration
- Use a prompt that explicitly states:
  - Canon is the only fact source.
  - Draft can only be used as reference.
  - Deprecated can only be used as historical conflict source.
  - Inspiration cannot be used as fact.
- Send the assembled context directly to the LLM for answering.

Advantages:

- Simple to implement.
- May perform well while the corpus is small.
- Allows the LLM to reason over broad context instead of isolated chunks.
- Useful as a debugging baseline for retrieval failures.

Risks:

- High token cost.
- Longer context can reduce consistency and attention.
- Draft or Deprecated content may contaminate answers despite prompt instructions.
- Less auditable than explicit evidence selection.
- Poor long-term fit as the project corpus grows.

### Mode B: Current RAG workflow

Definition:

- LLM-assisted query rewrite
- LlamaIndex BM25 retrieval
- Optional reranker / node postprocessor
- Evidence selection
- Context Pack assembly
- Canon / Draft / Deprecated / Inspiration separation
- Future QA / continuity reasoning over the Context Pack

Advantages:

- More scalable for a growing narrative corpus.
- More auditable because selected evidence is visible.
- Better control over which evidence enters the answer.
- Stronger governance of Canon / Draft / Deprecated boundaries.
- Better long-term fit for a collaborative narrative workflow.

Risks:

- Higher engineering complexity.
- Retrieval, chunking, and reranking require tuning.
- Evidence selector can choose the wrong chunks.
- For a small corpus, it may underperform direct full-context reading.

## 3. Unified Test Questions

Use the same test questions for both modes.

1. Rin是什么身份？
2. Mouse过去是什么身份？
3. Snow是什么实验对象？
4. Rain和Second Foundation是什么关系？
5. Judgment Day是什么事件？
6. Branch B中Rin哪条腿受伤？
7. 场景草稿风筝旧版可以覆盖当前Canon吗？
8. Rin喜欢什么音乐？
9. Mombasa安全屋是什么地方？
10. Tender is the Night酒吧有什么剧情作用？

## 4. Evaluation Metrics

Evaluate each question with the following dimensions:

- Answer correctness
- Source grounding
- Canon/Draft/Deprecated separation
- Deprecated contamination risk
- Missing evidence behavior
- Hallucination resistance
- Token cost estimate
- Latency
- Reproducibility
- Engineering complexity
- Portfolio value

Suggested scoring:

- `PASS`: Correct behavior with sufficient source grounding.
- `PARTIAL`: Useful answer, but incomplete, weakly grounded, or mildly contaminated.
- `FAIL`: Incorrect answer, unsupported claim, status violation, or hallucination.

## 5. Evaluation Table Template

Summary table:

| ID | Question | Mode A Result | Mode B Result | Correctness Winner | Grounding Winner | Notes |
|---|---|---|---|---|---|---|
| 1 | Rin是什么身份？ | TBD | TBD | TBD | TBD | TBD |
| 2 | Mouse过去是什么身份？ | TBD | TBD | TBD | TBD | TBD |
| 3 | Snow是什么实验对象？ | TBD | TBD | TBD | TBD | TBD |
| 4 | Rain和Second Foundation是什么关系？ | TBD | TBD | TBD | TBD | TBD |
| 5 | Judgment Day是什么事件？ | TBD | TBD | TBD | TBD | TBD |
| 6 | Branch B中Rin哪条腿受伤？ | TBD | TBD | TBD | TBD | TBD |
| 7 | 场景草稿风筝旧版可以覆盖当前Canon吗？ | TBD | TBD | TBD | TBD | TBD |
| 8 | Rin喜欢什么音乐？ | TBD | TBD | TBD | TBD | TBD |
| 9 | Mombasa安全屋是什么地方？ | TBD | TBD | TBD | TBD | TBD |
| 10 | Tender is the Night酒吧有什么剧情作用？ | TBD | TBD | TBD | TBD | TBD |

Detailed record template:

```markdown
## Test ID

Question:

Mode A Full-context Answer:

Mode A Sources:

Mode A Judgment:
PASS / PARTIAL / FAIL

Mode B RAG Context / Answer:

Mode B Sources:

Mode B Judgment:
PASS / PARTIAL / FAIL

Winner:

Notes:
```

## 6. Decision Rules

Use the comparison results to decide how each mode should be positioned.

If Full-context is clearly stronger on the current small corpus but has higher cost:

- Keep it as a baseline and debug mode.
- Use it to identify retrieval or chunking failures.
- Do not make it the long-term replacement for Context Pack governance.

If RAG is stronger on source grounding and version governance:

- Keep RAG + Context Pack as the main workflow.
- Improve retrieval precision, reranking, and evidence selection.
- Use Full-context only as a diagnostic comparator.

If the two modes have complementary strengths:

- Adopt hybrid routing.
- Use Full-context for small, bounded, exploratory questions.
- Use RAG for formal QA, continuity checks, and evidence-controlled outputs.

## 7. Proposed Hybrid Strategy

### Full-context mode

Use for:

- Small document subsets
- Quick validation
- Debugging retrieval failures
- Early creative exploration where broad context matters more than auditability

Expected behavior:

- Load status-grouped context.
- Preserve Canon / Draft / Deprecated / Inspiration instructions in the prompt.
- Report source groups used.
- Clearly mark when the answer depends on non-Canon material.

### RAG mode

Use for:

- Formal QA
- Continuity checking
- Multi-person collaboration
- Long-term knowledge base growth
- Portfolio-facing workflow demonstrations where auditability matters

Expected behavior:

- Retrieve and select evidence.
- Preserve status separation in Context Pack.
- Avoid using Draft / Deprecated / Inspiration as Canon facts.
- Return missing evidence when Canon support is insufficient.

### Comparison mode

Use for:

- Architecture evaluation
- Regression checks
- Retrieval tuning
- Demonstrating why the workflow uses Context Pack instead of raw LLM answers

Expected behavior:

- Run Full-context and RAG on the same question.
- Display both answers, sources, and status handling.
- Highlight disagreements.
- Mark the preferred result and the reason.

## 8. Future Implementation Plan

The following commands are possible future experiment commands. They are not part of this implementation step.

```powershell
E:\Desktop\python310\python.exe main.py context-full "问题"
E:\Desktop\python310\python.exe main.py ask-full "问题"
E:\Desktop\python310\python.exe main.py compare-rag-full "问题"
```

Possible future modules:

- `src/context/full_context_builder.py`
- `src/qa/full_context_qa.py`
- `src/eval/rag_vs_full_context.py`
- `tests/test_full_context_baseline.py`
- `tests/test_rag_vs_full_context_eval.py`

Future implementation constraints:

- Do not remove current RAG path.
- Do not bypass Canon / Draft / Deprecated governance.
- Do not use Full-context answers as ground truth without source judgment.
- Do not call external LLM APIs in default tests.
- Keep the comparison output inspectable and reproducible.

## Recommended Next Step

Create a manual evaluation sheet using the table above, then run the ten unified questions through:

1. Current `context-rag-llm` mode.
2. A manually assembled Full-context prompt.

Only after the result gaps are visible should the project add experimental CLI commands for Full-context or comparison mode.
