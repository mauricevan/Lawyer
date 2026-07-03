"""Unit tests for dependency readiness service (plan14 AA)."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.src.services.readiness_service import ReadinessService


def _service(postgres_ok: bool, qdrant_ok: bool, redis_ok: bool | None) -> ReadinessService:
    redis = MagicMock()
    if redis_ok is None:
        redis.health = AsyncMock(return_value={"enabled": False, "healthy": False})
    else:
        redis.health = AsyncMock(return_value={"enabled": True, "healthy": redis_ok})
    qdrant = MagicMock()
    if qdrant_ok:
        qdrant.health_check.return_value = {"healthy": True, "points_count": 10}
    else:
        qdrant.health_check.return_value = {"healthy": False, "error": "ConnectionError"}
    service = ReadinessService(redis_cache=redis, qdrant=qdrant)
    return service


@pytest.mark.asyncio
async def test_is_ready_when_tier1_healthy(monkeypatch):
    service = _service(postgres_ok=True, qdrant_ok=True, redis_ok=False)

    async def _ok_postgres():
        return {"status": "ok", "tier": 1, "required_for_ready": True}

    monkeypatch.setattr(service, "_check_postgres", _ok_postgres)
    checks = await service.run_checks()
    assert service.is_ready(checks) is True


@pytest.mark.asyncio
async def test_is_not_ready_when_postgres_fails(monkeypatch):
    service = _service(postgres_ok=False, qdrant_ok=True, redis_ok=True)

    async def _fail_postgres():
        return {"status": "error", "tier": 1, "required_for_ready": True}

    monkeypatch.setattr(service, "_check_postgres", _fail_postgres)
    checks = await service.run_checks()
    assert service.is_ready(checks) is False


@pytest.mark.asyncio
async def test_redis_error_does_not_block_ready(monkeypatch):
    service = _service(postgres_ok=True, qdrant_ok=True, redis_ok=False)

    async def _ok_postgres():
        return {"status": "ok", "tier": 1, "required_for_ready": True}

    monkeypatch.setattr(service, "_check_postgres", _ok_postgres)
    checks = await service.run_checks()
    assert checks["redis"]["status"] == "error"
    assert service.is_ready(checks) is True
