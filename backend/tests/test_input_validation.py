"""Tests for tightened API input validation."""
import pytest
from pydantic import ValidationError

from shared.schemas.query import QueryFilters, QueryRequest


def test_query_request_rejects_invalid_conversation_id() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(question="Wat is DORA?", conversation_id="not-a-uuid")


def test_query_filters_reject_invalid_celex() -> None:
    with pytest.raises(ValidationError):
        QueryFilters(celex="http://evil.test")


def test_query_filters_accept_valid_celex() -> None:
    filters = QueryFilters(celex="32022R2065")
    assert filters.celex == "32022R2065"


def test_query_request_rejects_invalid_language() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(question="Test vraag", language="nederlands")
