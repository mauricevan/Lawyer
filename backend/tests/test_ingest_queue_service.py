"""Tests for Celery ingest queue dispatch."""
import pytest

from backend.src.config import settings
from backend.src.services.ingest_queue_service import IngestQueueService


@pytest.mark.asyncio
async def test_enqueue_skips_when_celery_disabled(monkeypatch):
    monkeypatch.setattr(settings, "enable_celery_ingest", False)
    service = IngestQueueService()
    assert await service.enqueue_celex("32022R2554") is False


@pytest.mark.asyncio
async def test_enqueue_success(monkeypatch):
    monkeypatch.setattr(settings, "enable_celery_ingest", True)
    called: list[tuple[str, str]] = []
    service = IngestQueueService()
    monkeypatch.setattr(service, "_dispatch", lambda celex, profile: called.append((celex, profile)))
    assert await service.enqueue_celex("32022R2554") is True
    assert called == [("32022R2554", "high")]


@pytest.mark.asyncio
async def test_enqueue_reports_failure_when_worker_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "enable_celery_ingest", True)
    service = IngestQueueService()

    def _raise(_celex: str, _profile: str) -> None:
        raise RuntimeError("worker unavailable")

    monkeypatch.setattr(service, "_dispatch", _raise)
    assert await service.enqueue_celex("32022R2554") is False
