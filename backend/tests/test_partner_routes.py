"""API tests for partner routes (plan31 AA)."""
import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.main import app


@pytest.fixture
async def partner_client(monkeypatch):
    async def noop_init() -> None:
        return

    monkeypatch.setattr("backend.src.main.init_db", noop_init)
    monkeypatch.setenv("PARTNER_PILOT_API_KEY", "partner-test-key")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_partner_status_requires_key(partner_client):
    response = await partner_client.get("/api/v1/partner/status")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_partner_status_ok_with_key(partner_client):
    response = await partner_client.get(
        "/api/v1/partner/status",
        headers={"X-Partner-Key": "partner-test-key"},
    )
    assert response.status_code == 200
    assert response.json()["partner_id"] == "pilot-partner"
