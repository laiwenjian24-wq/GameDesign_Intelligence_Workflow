from src.v1.ingestion.status_policy import (
    can_enter_canon_context,
    is_reference_only,
    is_warning_only,
)


def test_only_canon_can_enter_canon_context():
    assert can_enter_canon_context("canon") is True
    assert can_enter_canon_context("draft") is False
    assert can_enter_canon_context("deprecated") is False
    assert can_enter_canon_context("inspiration") is False
    assert can_enter_canon_context("unknown") is False


def test_non_canon_status_roles():
    assert is_warning_only("deprecated") is True
    assert is_reference_only("draft") is True
    assert is_reference_only("canon") is False
