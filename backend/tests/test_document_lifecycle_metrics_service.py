"""Unit tests for lifecycle metrics aggregation (plan13 AD)."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.src.services.document_lifecycle_metrics_service import DocumentLifecycleMetricsService


@pytest.mark.asyncio
async def test_build_summary_includes_core_sections(monkeypatch):
    service = DocumentLifecycleMetricsService()
    monkeypatch.setattr(service._staleness, "scan", AsyncMock(return_value=[]))
    monkeypatch.setattr(service._versions, "scan_indexed", AsyncMock(return_value=[]))
    session = MagicMock()
    count_result = MagicMock()
    count_result.scalar.return_value = 12
    session.execute = AsyncMock(return_value=count_result)
    summary = await service.build_summary(session)
    assert "staleness" in summary
    assert "deprecation" in summary
    assert "version_conflicts" in summary
    assert "coverage" in summary
    assert summary["coverage"]["indexed_count"] == 12
