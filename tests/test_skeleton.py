"""Skeleton tests.

These tests intentionally verify only that the project skeleton can be imported.
Real behavior tests should be added when ingestion and retrieval are implemented.
"""


def test_skeleton_imports() -> None:
    from src.metadata.schema import AssetClass, build_empty_metadata

    metadata = build_empty_metadata()

    assert metadata["status"] == AssetClass.UNKNOWN.value
