"""API tests for /ready readiness endpoint (plan14 AA)."""
import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.main import app


@pytest.fixture
async def health_client(monkeypatch):
    async def noop_init() -> None:
        return

    monkeypatch.setattr("backend.src.main.init_db", noop_init)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_ready_returns_200_when_tier1_healthy(health_client, monkeypatch):
    async def _ready_report():
        return {"status": "ready", "checks": {}, "tier1_ok": True, "metrics": {}}

    monkeypatch.setattr(
        "backend.src.routes.health._readiness.build_report",
        _ready_report,
    )
    response = await health_client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_ready_returns_503_when_degraded(health_client, monkeypatch):
    async def _degraded_report():
        return {"status": "degraded", "checks": {}, "tier1_ok": False, "metrics": {}}

    monkeypatch.setattr(
        "backend.src.routes.health._readiness.build_report",
        _degraded_report,
    )
    response = await health_client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
