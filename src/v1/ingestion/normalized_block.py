"""Normalized document block schema for v1 ingestion."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NormalizedBlock:
    block_id: str
    source_file: str
    original_path: str
    status: str
    document_type: str
    section_title: str
    heading_path: List[str]
    block_type: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    page_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
