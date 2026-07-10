# RAGFlow Evidence Adapter Contract

## Input

RAGFlow retrieval response.

The exact field names must be confirmed during evaluation. The adapter should expect at minimum:

- Retrieved text or chunk content.
- Source document name or URI.
- Retrieval score if available.
- Page number or chunk id if available.
- Parser metadata if available.

## Output

Normalized evidence items compatible with `src/v1`.

Required fields:

- `evidence_id`
- `text`
- `source_file`
- `source_uri` optional
- `page_number` optional
- `chunk_id` optional
- `retrieval_score` optional
- `status`
- `status_source`
- `document_type`
- `section_title` optional
- `metadata`

## Status Resolution

RAGFlow does not decide status.

Status must come from:

1. `import_manifest`
2. Metadata mapping
3. Manual fallback as `unknown`

If status cannot be resolved, evidence must be marked `unknown` and require human review.

## Source Policy

- Canon can support current facts.
- Draft is reference only.
- Deprecated is historical/conflict evidence only.
- Inspiration is not fact.
- Unknown requires review.

## Future Adapter

Future code may create:

```text
src/v1/backends/ragflow_adapter.py
```

This evaluation step does not create adapter code.
