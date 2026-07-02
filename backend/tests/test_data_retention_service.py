"""Tests for data retention service."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.src.config import settings
from backend.src.services.data_retention_service import DataRetentionService


def test_cutoff_respects_days(monkeypatch):
    monkeypatch.setattr(settings, "query_log_retention_days", 45)
    service = DataRetentionService()
    now = datetime(2026, 7, 1, tzinfo=timezone.utc)
    assert service.cutoff(45, now).date().isoformat() == "2026-05-17"


@pytest.mark.asyncio
async def test_purge_expired_returns_counts(monkeypatch):
    monkeypatch.setattr(settings, "query_log_retention_days", 90)
    monkeypatch.setattr(settings, "feedback_retention_days", 365)
    monkeypatch.setattr(settings, "conversation_retention_days", 180)
    service = DataRetentionService()
    session = AsyncMock()
    result = MagicMock()
    result.rowcount = 2
    session.execute = AsyncMock(return_value=result)
    removed = await service.purge_expired(session)
    assert removed["query_logs"] == 2
    assert removed["conversations"] == 2
    session.commit.assert_awaited_once()
