"""Unit tests for lifecycle reindex candidate selection (plan13 AB)."""
from datetime import datetime, timedelta, timezone

from backend.src.models.tables import Document
from backend.src.services.document_reindex_service import DocumentReindexService


NOW = datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc)


def _document(
    *,
    indexed_at: datetime | None = None,
    modified_at: datetime | None = None,
) -> Document:
    return Document(
        celex="32022R2554",
        language="nl",
        title="Test regulation",
        indexed_at=indexed_at,
        modified_at=modified_at,
    )


def test_reindex_reason_modified_drift():
    service = DocumentReindexService(now=NOW)
    indexed_at = NOW - timedelta(days=2)
    modified_at = NOW - timedelta(hours=1)
    reason = service.reindex_reason(_document(indexed_at=indexed_at, modified_at=modified_at))
    assert reason == "modified_drift"


def test_reindex_reason_never_indexed():
    service = DocumentReindexService(now=NOW)
    assert service.reindex_reason(_document()) == "never_indexed"


def test_reindex_reason_fresh_document():
    service = DocumentReindexService(now=NOW)
    indexed_at = NOW - timedelta(hours=1)
    modified_at = NOW - timedelta(hours=2)
    assert service.reindex_reason(_document(indexed_at=indexed_at, modified_at=modified_at)) is None


def test_evaluate_sla_passes_within_window():
    service = DocumentReindexService(now=NOW)
    candidate = service._candidate(
        _document(
            indexed_at=NOW - timedelta(days=2),
            modified_at=NOW - timedelta(hours=24),
        )
    )
    assert candidate is not None
    sla = service.evaluate_sla([candidate])
    assert sla["passed"] is True


def test_evaluate_sla_fails_when_drift_exceeds_limit():
    service = DocumentReindexService(now=NOW)
    candidate = service._candidate(
        _document(
            indexed_at=NOW - timedelta(days=10),
            modified_at=NOW - timedelta(days=5),
        )
    )
    assert candidate is not None
    sla = service.evaluate_sla([candidate])
    assert sla["passed"] is False
    assert sla["violation_count"] == 1
