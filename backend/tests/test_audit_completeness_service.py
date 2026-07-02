"""Tests for audit completeness validation."""
from backend.src.models.tables import AuditLog
from backend.src.services.audit_completeness_service import is_audit_entry_complete, summarize_completeness


def _entry(**kwargs) -> AuditLog:
    defaults = {
        "request_id": "req-1",
        "question": "Wat is DORA?",
        "route": {"retrieval_route": "hybrid"},
        "model": "test-model",
    }
    defaults.update(kwargs)
    return AuditLog(**defaults)


def test_complete_entry_passes_validation():
    assert is_audit_entry_complete(_entry())


def test_missing_route_fails_validation():
    assert not is_audit_entry_complete(_entry(route=None))


def test_summarize_completeness_calculates_ratio():
    summary = summarize_completeness([
        _entry(),
        _entry(route={"retrieval_route": ""}),
    ])
    assert summary["count"] == 2
    assert summary["complete"] == 1
    assert summary["completeness_ratio"] == 0.5
