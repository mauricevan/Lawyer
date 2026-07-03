"""Tests for query filter sanitization."""
from backend.src.utils.query_filter_sanitizer import sanitize_query_request
from shared.schemas.query import QueryFilters, QueryRequest


def test_include_deprecated_stripped_for_user_role():
    request = QueryRequest(
        question="What is GDPR?",
        filters=QueryFilters(include_deprecated=True),
    )
    sanitized = sanitize_query_request(request, "user")
    assert sanitized.filters is not None
    assert sanitized.filters.include_deprecated is False


def test_include_deprecated_kept_for_analyst_role():
    request = QueryRequest(
        question="What is GDPR?",
        filters=QueryFilters(include_deprecated=True),
    )
    sanitized = sanitize_query_request(request, "analyst")
    assert sanitized.filters is not None
    assert sanitized.filters.include_deprecated is True
