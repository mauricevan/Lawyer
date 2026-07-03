"""Unit tests for document index staleness detection (plan13 AA)."""
from datetime import datetime, timedelta, timezone

from backend.src.models.tables import Document
from backend.src.services.document_staleness_service import DocumentStalenessService
from backend.src.utils.document_lifecycle_config import load_document_lifecycle_policy, scan_gates


NOW = datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc)


def _document(
    *,
    indexed_at: datetime | None = None,
    modified_at: datetime | None = None,
    celex: str = "32022R2554",
) -> Document:
    return Document(
        celex=celex,
        language="nl",
        title="Test regulation",
        indexed_at=indexed_at,
        modified_at=modified_at,
    )


def test_classify_never_indexed():
    service = DocumentStalenessService(now=NOW)
    record = service._classify(_document())
    assert record.status == "never_indexed"


def test_classify_fresh_index():
    service = DocumentStalenessService(now=NOW)
    indexed_at = NOW - timedelta(hours=24)
    record = service._classify(_document(indexed_at=indexed_at))
    assert record.status == "fresh"
    assert record.index_age_hours == 24.0


def test_classify_stale_by_age():
    service = DocumentStalenessService(now=NOW)
    indexed_at = NOW - timedelta(hours=200)
    record = service._classify(_document(indexed_at=indexed_at))
    assert record.status == "stale"


def test_classify_critical_by_age():
    service = DocumentStalenessService(now=NOW)
    indexed_at = NOW - timedelta(hours=800)
    record = service._classify(_document(indexed_at=indexed_at))
    assert record.status == "critical"


def test_classify_modified_drift_is_stale():
    service = DocumentStalenessService(now=NOW)
    indexed_at = NOW - timedelta(hours=24)
    modified_at = NOW - timedelta(hours=1)
    record = service._classify(_document(indexed_at=indexed_at, modified_at=modified_at))
    assert record.status == "stale"
    assert record.modified_drift_hours == 23.0


def test_summarize_counts_statuses():
    service = DocumentStalenessService(now=NOW)
    records = [
        service._classify(_document(indexed_at=NOW - timedelta(hours=1))),
        service._classify(_document(indexed_at=NOW - timedelta(hours=200))),
        service._classify(_document()),
    ]
    summary = service.summarize(records)
    assert summary["total_documents"] == 3
    assert summary["fresh"] == 1
    assert summary["stale"] == 1
    assert summary["never_indexed"] == 1


def test_evaluate_gates_passes_clean_summary():
    service = DocumentStalenessService(now=NOW)
    summary = {"fresh": 5, "stale": 0, "critical": 0, "never_indexed": 0}
    gate = service.evaluate_gates(summary)
    assert gate["passed"] is True


def test_evaluate_gates_fails_on_never_indexed():
    service = DocumentStalenessService(now=NOW)
    summary = {"fresh": 1, "stale": 0, "critical": 0, "never_indexed": 2}
    gate = service.evaluate_gates(summary)
    assert gate["passed"] is False
    assert any("never_indexed" in failure for failure in gate["failures"])


def test_lifecycle_policy_loads():
    policy = load_document_lifecycle_policy()
    assert policy["staleness"]["max_index_age_hours"] == 168
    assert scan_gates()["max_never_indexed"] == 0
