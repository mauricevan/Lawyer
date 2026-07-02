"""Tests for feedback API."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.main import app
from backend.src.routes import feedback as feedback_route


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
async def feedback_client(mock_session, monkeypatch):
    async def noop_init() -> None:
        return

    monkeypatch.setattr("backend.src.main.init_db", noop_init)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[feedback_route.get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_submit_feedback_accepts_taxonomy(feedback_client):
    response = await feedback_client.post(
        "/api/v1/feedback",
        json={
            "rating": 2,
            "category": "source_issue",
            "comment": "Verkeerde CELEX",
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "received"


@pytest.mark.asyncio
async def test_submit_feedback_rejects_invalid_category(feedback_client):
    response = await feedback_client.post(
        "/api/v1/feedback",
        json={"rating": 3, "category": "spam"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_submit_feedback_rejects_invalid_rating(feedback_client):
    response = await feedback_client.post(
        "/api/v1/feedback",
        json={"rating": 0, "category": "ux"},
    )
    assert response.status_code == 422
