"""Build a candidate JSON Context Pack from normalized blocks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.normalized_context_adapter.build_context_pack_from_blocks import (  # noqa: E402
    build_context_pack as build_adapter_context_pack,
)
from experiments.normalized_context_adapter.normalized_block_loader import (  # noqa: E402
    DEFAULT_BLOCKS_PATH,
    NormalizedBlocksMissingError,
    missing_blocks_message,
)

try:
    from .context_pack_schema import (  # type: ignore
        ContextPack,
        MissingEvidence,
        build_diagnostics,
        default_metadata,
        evidence_from_adapter_item,
    )
except ImportError:  # pragma: no cover - direct script execution
    from context_pack_schema import (
        ContextPack,
        MissingEvidence,
        build_diagnostics,
        default_metadata,
        evidence_from_adapter_item,
    )


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = EXPERIMENT_DIR / "sample_outputs" / "context_pack.json"


GROUP_TO_STATUS = {
    "canon_context": "canon",
    "draft_reference": "draft",
    "deprecated_warnings": "deprecated",
    "inspiration_reference": "inspiration",
}


def _convert_group(items: List[Dict[str, Any]], prefix: str) -> List[Any]:
    converted = []
    for index, item in enumerate(items, start=1):
        converted.append(evidence_from_adapter_item(item, f"{prefix}-{index:04d}"))
    return converted


def build_json_context_pack(
    query: str,
    blocks_path: Path = DEFAULT_BLOCKS_PATH,
    task_type: str | None = None,
) -> Dict[str, Any]:
    adapter_pack = build_adapter_context_pack(query, blocks_path=blocks_path)
    groups = adapter_pack.get("groups", {})
    canon_context = _convert_group(groups.get("canon_context", []), "canon")
    draft_reference = _convert_group(groups.get("draft_reference", []), "draft")
    deprecated_warnings = _convert_group(groups.get("deprecated_warnings", []), "deprecated")
    inspiration_reference = _convert_group(groups.get("inspiration_reference", []), "inspiration")

    missing_evidence = [
        MissingEvidence(
            description=str(item),
            severity="high",
            suggested_next_step="Review normalized blocks or expand ingestion sample before making a current-truth decision.",
        )
        for item in adapter_pack.get("missing_evidence", [])
    ]
    if not canon_context and not missing_evidence:
        missing_evidence.append(
            MissingEvidence(
                description="No canon evidence found in normalized Context Pack.",
                severity="high",
                suggested_next_step="Retrieve or ingest Canon material before answering as current truth.",
            )
        )

    diagnostics = build_diagnostics(
        canon_context,
        draft_reference,
        deprecated_warnings,
        inspiration_reference,
    )
    context_pack = ContextPack(
        query=query,
        task_type=task_type,
        canon_context=canon_context,
        draft_reference=draft_reference,
        deprecated_warnings=deprecated_warnings,
        inspiration_reference=inspiration_reference,
        missing_evidence=missing_evidence,
        source_summary=adapter_pack.get("source_summary", []),
        diagnostics=diagnostics,
        metadata=default_metadata(),
    )
    return context_pack.to_dict()


def write_context_pack(payload: Dict[str, Any], output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def run(
    query: str,
    blocks_path: Path = DEFAULT_BLOCKS_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    task_type: str | None = None,
) -> Path:
    payload = build_json_context_pack(query, blocks_path=blocks_path, task_type=task_type)
    return write_context_pack(payload, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build candidate JSON Context Pack.")
    parser.add_argument("query")
    parser.add_argument("--task-type", default=None)
    parser.add_argument("--blocks", type=Path, default=DEFAULT_BLOCKS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    try:
        output_path = run(args.query, blocks_path=args.blocks, output_path=args.output, task_type=args.task_type)
    except NormalizedBlocksMissingError:
        print(missing_blocks_message(args.blocks))
        return 1
    print(f"Wrote JSON Context Pack: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
