# V1 Lite Knowledge Base MVP

## Purpose

The project is not using RAGFlow, Dify, Docker, GraphRAG, Haystack, or an image generation backend for this MVP.

The goal is a lightweight terminal workflow:

```text
documents
-> NormalizedBlock
-> lightweight knowledge index
-> chat retrieval
-> fake / DeepSeek output
```

## Supported File Types

Current MVP:

- Markdown: `.md`
- Word: `.docx`
- PDF: `.pdf`
- Plain text: `.txt`

Temporarily out of scope:

- Ren'Py `.rpy`
- PNG visual understanding
- GraphRAG
- RAGFlow / Dify

## Parser Strategy

Preferred parser for `.docx` and `.pdf`:

```powershell
E:\Desktop\python310\python.exe -m pip install markitdown pymupdf
```

Parser order:

1. `.md` / `.txt`: direct text read.
2. `.docx` / `.pdf`: MarkItDown.
3. `.pdf`: PyMuPDF fallback.
4. Unsupported or missing parser: graceful warning, no crash.

Tests do not require MarkItDown or PyMuPDF.

## Canon Governance

Parsers do not decide status.

Status comes from:

1. `import_manifest`
2. Existing metadata mapping
3. `unknown`

DeepSeek may generate answers or briefs only when explicitly selected. It cannot automatically canonize new material.
