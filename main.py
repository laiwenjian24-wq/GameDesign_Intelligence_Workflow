"""Entry point for the first Narrative Workflow MVP.

Current first-version behavior:

1. Markdown / TXT ingestion
2. rule-based metadata draft generation
3. JSONL output to knowledge_base/processed/metadata.jsonl
4. keyword search over metadata and raw source text

No LLM call, vector index, or complex RAG logic is implemented here.
"""

from pathlib import Path
import sys

from src.context.context_builder import (
    build_context_pack,
    format_context_pack_markdown,
)
from src.retrieval.index_builder import build_index
from src.retrieval.query import query_knowledge_base
from src.workflows.continuity_checker import (
    format_continuity_report,
    run_continuity_check,
)
from src.workflows.ingest_workflow import run_ingestion_workflow


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_ASSETS_DIR = PROJECT_ROOT / "knowledge_base" / "raw_assets"
PROCESSED_DIR = PROJECT_ROOT / "knowledge_base" / "processed"
INDEX_DIR = PROJECT_ROOT / "knowledge_base" / "index"


def run_ingestion() -> None:
    """Run one ingestion pass for Markdown and TXT assets."""
    records = run_ingestion_workflow(RAW_ASSETS_DIR, PROCESSED_DIR)
    output_path = PROCESSED_DIR / "metadata.jsonl"

    print("STUPID Narrative Workflow ingestion completed.")
    print(f"Raw assets directory: {RAW_ASSETS_DIR}")
    print(f"Processed metadata: {output_path}")
    print(f"Records written: {len(records)}")


def run_search(query: str) -> None:
    """Run one keyword search against the local narrative knowledge base."""
    run_ingestion_workflow(RAW_ASSETS_DIR, PROCESSED_DIR)
    build_index(PROCESSED_DIR, INDEX_DIR)

    results = query_knowledge_base(query, INDEX_DIR, top_k=5)

    print(f"Search query: {query}")
    print(f"Results: {len(results)}")

    if not results:
        print("No matching narrative assets found.")
        return

    for index, result in enumerate(results, start=1):
        print("")
        print(f"[{index}] {result['filename']}")
        print(f"status: {result['status']}")
        print(f"summary: {result['summary']}")
        print(f"source_file: {result['source_file']}")
        print(f"excerpt: {result['excerpt']}")
        print(f"reason_used: {result['reason_used']}")


def run_check(input_text: str) -> None:
    """Run rule-based continuity checking against local indexed assets."""
    run_ingestion_workflow(RAW_ASSETS_DIR, PROCESSED_DIR)
    build_index(PROCESSED_DIR, INDEX_DIR)

    report = run_continuity_check(input_text, INDEX_DIR, top_k=5)
    print(format_continuity_report(report))


def run_context(task: str) -> None:
    """Build and print a Narrative Context Pack."""
    run_ingestion_workflow(RAW_ASSETS_DIR, PROCESSED_DIR)
    build_index(PROCESSED_DIR, INDEX_DIR)

    context_pack = build_context_pack(task, INDEX_DIR, top_k=5)
    print(format_context_pack_markdown(context_pack))


def main() -> None:
    """Run ingestion by default, search, continuity check, or context pack."""
    if len(sys.argv) >= 2 and sys.argv[1] == "ingest":
        run_ingestion()
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        run_search(" ".join(sys.argv[2:]))
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "check":
        run_check(" ".join(sys.argv[2:]))
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "context":
        run_context(" ".join(sys.argv[2:]))
        return

    run_ingestion()


if __name__ == "__main__":
    main()
