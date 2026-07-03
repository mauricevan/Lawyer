"""Unit tests for document deprecation register (plan13 AC)."""
from backend.src.services.document_deprecation_service import DocumentDeprecationService
from backend.src.utils.qdrant_filters import build_qdrant_filter
from shared.schemas.query import QueryFilters


def test_soft_deprecated_excluded_by_default():
    service = DocumentDeprecationService()
    assert service.is_excluded("32014R0330", "nl", None) is True


def test_explicit_celex_filter_allows_deprecated_lookup():
    service = DocumentDeprecationService()
    filters = QueryFilters(celex="32014R0330")
    assert service.is_excluded("32014R0330", "nl", filters) is False


def test_include_deprecated_bypasses_exclusion():
    service = DocumentDeprecationService()
    filters = QueryFilters(include_deprecated=True)
    assert service.is_excluded("32014R0330", "nl", filters) is False


def test_filter_chunks_removes_deprecated():
    service = DocumentDeprecationService()
    chunks = [
        {"chunk_id": "a", "celex": "32014R0330", "language": "nl"},
        {"chunk_id": "b", "celex": "32022R2554", "language": "nl"},
    ]
    filtered = service.filter_chunks(chunks, None)
    assert len(filtered) == 1
    assert filtered[0]["celex"] == "32022R2554"


def test_qdrant_filter_excludes_deprecated_celex():
    query_filter = build_qdrant_filter(None, "nl", True, {"32014R0330"})
    assert query_filter is not None
    assert query_filter.must_not


def test_summarize_lists_registered_entries():
    summary = DocumentDeprecationService().summarize()
    assert summary["registered"] >= 1
    assert "32014R0330" in summary["search_excluded_celex"]
