"""Tests for PostgreSQL FTS search SQL."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.src.services.postgres_search_service import PostgresSearchService


@pytest.mark.asyncio
async def test_search_uses_any_for_excluded_celex():
    session = MagicMock()
    nested = AsyncMock()
    session.begin_nested.return_value.__aenter__ = AsyncMock(return_value=nested)
    session.begin_nested.return_value.__aexit__ = AsyncMock(return_value=None)
    result = MagicMock()
    result.mappings.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    service = PostgresSearchService()
    await service.search(session, "DORA financiële instellingen", "nl", excluded_celex={"32022R2554"})

    sql = str(session.execute.call_args[0][0])
    params = session.execute.call_args[0][1]
    assert "ANY(:excluded_celex)" in sql
    assert params["excluded_celex"] == ["32022R2554"]


@pytest.mark.asyncio
async def test_search_omits_exclusion_when_empty():
    session = MagicMock()
    nested = AsyncMock()
    session.begin_nested.return_value.__aenter__ = AsyncMock(return_value=nested)
    session.begin_nested.return_value.__aexit__ = AsyncMock(return_value=None)
    result = MagicMock()
    result.mappings.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    service = PostgresSearchService()
    await service.search(session, "douane regels", "nl", excluded_celex=set())

    sql = str(session.execute.call_args[0][0])
    assert "excluded_celex" not in sql


@pytest.mark.asyncio
async def test_search_returns_empty_on_failure():
    session = MagicMock()
    session.begin_nested.side_effect = RuntimeError("syntax error")
    service = PostgresSearchService()
    rows = await service.search(session, "test query", "nl")
    assert rows == []
