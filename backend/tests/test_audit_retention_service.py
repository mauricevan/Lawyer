"""Tests for audit retention service."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.src.config import settings
from backend.src.services.audit_retention_service import AuditRetentionService


def test_cutoff_uses_configured_days(monkeypatch):
    monkeypatch.setattr(settings, "audit_retention_days", 30)
    service = AuditRetentionService()
    now = datetime(2026, 7, 1, tzinfo=timezone.utc)
    assert service.cutoff(now).date().isoformat() == "2026-06-01"


@pytest.mark.asyncio
async def test_purge_expired_commits_delete(monkeypatch):
    monkeypatch.setattr(settings, "audit_retention_days", 90)
    service = AuditRetentionService()
    session = AsyncMock()
    result = MagicMock()
    result.rowcount = 3
    session.execute = AsyncMock(return_value=result)
    removed = await service.purge_expired(session)
    assert removed == 3
    session.commit.assert_awaited_once()
