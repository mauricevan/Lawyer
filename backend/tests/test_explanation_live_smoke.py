"""Live API smoke — requires backend on :8000 (skip when unavailable)."""
from __future__ import annotations

import os

import httpx
import pytest

from backend.src.utils.explanation_authority_guard import has_authority_leak

_FORBIDDEN_IN_ANSWER = (
    "hof-simulatie",
    "eu besluitvorming",
    "majority opinion",
    "doctrine-evolutie",
    "the measure constitutes",
    "juridisch effect",
)


def _backend_ok() -> bool:
    try:
        return httpx.get("http://localhost:8000/health", timeout=3.0).status_code == 200
    except httpx.HTTPError:
        return False


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("EXPLANATION_LIVE_SMOKE") != "1" or not _backend_ok(),
    reason="Set EXPLANATION_LIVE_SMOKE=1 with backend on :8000",
)
def test_c3_two_turn_answer_has_no_judicial_leak() -> None:
    """C3 flow: platform question → chip answer must stay explanation-only."""
    base = "http://localhost:8000/api/v1"
    with httpx.Client(timeout=120.0) as client:
        conv = client.post(f"{base}/conversations", json={"query_mode": "open"}).json()["id"]
        turn1 = client.post(
            f"{base}/query",
            json={
                "question": "Mag ik een platform beginnen?",
                "conversation_id": conv,
                "language": "nl",
                "audience": "layperson",
            },
        ).json()
        chips = turn1.get("verification_questions") or []
        chip = next(
            (c for c in chips if "website" in c.lower() or "content" in c.lower()),
            chips[0] if chips else "contentwebsite",
        )
        turn2 = client.post(
            f"{base}/query",
            json={
                "question": chip,
                "conversation_id": conv,
                "language": "nl",
                "audience": "layperson",
            },
        ).json()
    answer = (turn2.get("answer") or "").lower()
    assert has_authority_leak(answer) is False
    for token in _FORBIDDEN_IN_ANSWER:
        assert token not in answer, token
    assert turn2.get("coverage_status") in {"adequate", "insufficient", "clarify_only"}
