"""Entry point for the Narrative Workflow CLI.

The default no-argument command still runs the original ingestion workflow.
"""

from pathlib import Path
import sys
from typing import List

from src.context.context_builder import (
    build_context_pack,
    format_context_pack_markdown,
)
from src.context.llamaindex_context_builder import build_context_pack_with_llamaindex
from src.llm.client import DeepSeekLLMClient, FakeLLMClient, LLMProviderError
from src.rag.llamaindex_ingest import build_llamaindex_nodes
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
LLAMA_INDEX_DIR = PROJECT_ROOT / "knowledge_base" / "llama_index"

AVAILABLE_COMMANDS = [
    "ingest",
    "search",
    "context",
    "context-rag",
    "context-rag-llm",
    "check",
]


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


def _append_rag_evidence(lines: List[str], citations: List[dict]) -> None:
    """Append RAG evidence with score and text excerpt."""
    if not citations:
        lines.append("- None")
        return

    for citation in citations:
        metadata = citation.get("metadata", {})
        lines.append(f"- source_file: {citation.get('source_file', '')}")
        lines.append(f"  - status: {citation.get('status', 'unknown')}")
        lines.append(f"  - score: {citation.get('score', 0)}")
        if metadata.get("heading"):
            lines.append(f"  - heading: {metadata.get('heading', '')}")
        if metadata.get("section_title"):
            lines.append(f"  - section_title: {metadata.get('section_title', '')}")
        lines.append(f"  - retrieval_mode: {citation.get('retrieval_mode', 'unknown')}")
        lines.append(
            f"  - used_real_llamaindex: {citation.get('used_real_llamaindex', False)}"
        )
        lines.append(f"  - fallback: {citation.get('fallback', True)}")
        lines.append(f"  - excerpt: {citation.get('excerpt', '')}")
        text = citation.get("text", "")
        if text:
            compact_text = " ".join(text.split())
            lines.append(f"  - text: {compact_text[:260]}")
        if citation.get("reason_used"):
            lines.append(f"  - reason_used: {citation.get('reason_used', '')}")


def format_llamaindex_context_report(context_pack: dict) -> str:
    """Format an experimental LlamaIndex Context Pack for CLI output."""
    task_context = context_pack.get("task_context", {})
    retrieval_metadata = context_pack.get("retrieval_metadata", {})
    lines = [
        "# Experimental RAG Context Pack",
        "",
        "## Task",
        f"- {task_context.get('task', '')}",
        "",
        "## Retrieval",
        f"- retrieval_mode: {retrieval_metadata.get('retrieval_mode', 'unknown')}",
        f"- used_real_llamaindex: {retrieval_metadata.get('used_real_llamaindex', False)}",
        f"- fallback: {retrieval_metadata.get('fallback', True)}",
        "",
    ]

    retrieval_plan = context_pack.get("retrieval_plan")
    if retrieval_plan:
        lines.extend(
            [
                "## Retrieval Plan",
                f"- intent: {retrieval_plan.get('intent', '')}",
                f"- entities: {', '.join(retrieval_plan.get('entities', []))}",
                "- rewritten_queries:",
            ]
        )
        for query in retrieval_plan.get("rewritten_queries", []):
            lines.append(f"  - {query}")
        lines.extend(
            [
                f"- forbidden_fact_statuses: {', '.join(retrieval_plan.get('forbidden_fact_statuses', []))}",
                f"- confidence: {retrieval_plan.get('confidence', '')}",
                "",
            ]
        )

    lines.append("## Canon Context")

    _append_rag_evidence(lines, context_pack.get("canon_context", []))

    lines.extend(["", "## Draft Reference"])
    _append_rag_evidence(lines, context_pack.get("draft_reference", []))

    lines.extend(["", "## Deprecated Warnings"])
    _append_rag_evidence(lines, context_pack.get("deprecated_warnings", []))

    lines.extend(["", "## Missing Evidence"])
    missing = context_pack.get("missing_evidence", [])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- None")

    lines.extend(["", "## Restrictions"])
    for restriction in context_pack.get("restrictions", []):
        lines.append(f"- {restriction}")

    selection = context_pack.get("llm_evidence_selection")
    if selection:
        lines.extend(["", "## Rejected Evidence"])
        rejected = selection.get("rejected", [])
        if rejected:
            for item in rejected:
                lines.append(
                    f"- {item.get('source_file', '')} [{item.get('status', 'unknown')}]: "
                    f"{item.get('reason', '')}"
                )
        else:
            lines.append("- None")

    return "\n".join(lines)


def run_context_rag(task: str) -> None:
    """Build and print an experimental LlamaIndex-backed Context Pack."""
    build_llamaindex_nodes(index_dir=LLAMA_INDEX_DIR)
    context_pack = build_context_pack_with_llamaindex(
        task,
        top_k=8,
        index_dir=LLAMA_INDEX_DIR,
    )
    print(format_llamaindex_context_report(context_pack))


def _llm_client_for_provider(provider: str):
    """Return the configured LLM client for a CLI provider name."""
    if provider == "fake":
        return FakeLLMClient()
    if provider == "deepseek":
        return DeepSeekLLMClient()
    raise LLMProviderError(
        f"Unknown LLM provider: {provider}. Available providers: fake, deepseek."
    )


def _extract_provider(args: List[str]) -> tuple:
    """Extract --provider from command arguments."""
    provider = "fake"
    remaining = []
    index = 0
    while index < len(args):
        item = args[index]
        if item == "--provider":
            if index + 1 >= len(args):
                raise LLMProviderError("--provider requires a value: fake or deepseek.")
            provider = args[index + 1]
            index += 2
            continue
        remaining.append(item)
        index += 1
    return provider, remaining


def run_context_rag_llm(task: str, provider: str = "fake") -> None:
    """Build and print an LLM-assisted LlamaIndex Context Pack."""
    build_llamaindex_nodes(index_dir=LLAMA_INDEX_DIR)
    llm_client = _llm_client_for_provider(provider)
    context_pack = build_context_pack_with_llamaindex(
        task,
        top_k=8,
        index_dir=LLAMA_INDEX_DIR,
        use_llm_assist=True,
        llm_client=llm_client,
    )
    print(format_llamaindex_context_report(context_pack))


def print_available_commands() -> None:
    """Print available CLI commands."""
    print("Available commands:")
    for command in AVAILABLE_COMMANDS:
        print(f"- {command}")


def dispatch(argv: List[str]) -> int:
    """Dispatch CLI arguments and return a process exit code."""
    if not argv:
        run_ingestion()
        return 0

    command = argv[0]

    if command == "ingest":
        run_ingestion()
        return 0

    if command == "search" and len(argv) >= 2:
        run_search(" ".join(argv[1:]))
        return 0

    if command == "check" and len(argv) >= 2:
        run_check(" ".join(argv[1:]))
        return 0

    if command == "context" and len(argv) >= 2:
        run_context(" ".join(argv[1:]))
        return 0

    if command == "context-rag" and len(argv) >= 2:
        run_context_rag(" ".join(argv[1:]))
        return 0

    if command == "context-rag-llm" and len(argv) >= 2:
        try:
            provider, task_args = _extract_provider(argv[1:])
            if not task_args:
                raise LLMProviderError("context-rag-llm requires a question.")
            run_context_rag_llm(" ".join(task_args), provider=provider)
            return 0
        except LLMProviderError as exc:
            print(str(exc))
            return 1

    print(f"Unknown command: {command}")
    print_available_commands()
    return 1


def main() -> None:
    """Run the CLI."""
    raise SystemExit(dispatch(sys.argv[1:]))


if __name__ == "__main__":
    main()
