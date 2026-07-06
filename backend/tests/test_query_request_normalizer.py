"""Tests for query request language normalization."""
from backend.src.utils.query_request_normalizer import normalize_query_request
from shared.schemas.query import QueryFilters, QueryRequest


def test_auto_language_resolves_to_detected_nl() -> None:
    request = QueryRequest(question="mag ik een platform bouwen", language="auto")
    normalized = normalize_query_request(request)
    assert normalized.language == "nl"


def test_auto_filter_language_resolves() -> None:
    request = QueryRequest(
        question="mag ik een platform bouwen",
        language="nl",
        filters=QueryFilters(language="auto"),
    )
    normalized = normalize_query_request(request)
    assert normalized.filters is not None
    assert normalized.filters.language == "nl"


def test_explicit_language_is_unchanged() -> None:
    request = QueryRequest(question="What does GDPR require?", language="en")
    normalized = normalize_query_request(request)
    assert normalized.language == "en"
