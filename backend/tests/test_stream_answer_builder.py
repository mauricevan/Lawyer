"""Tests for stream answer builder."""
from backend.src.utils.stream_answer_builder import answer_from_stream_detail


def test_answer_from_stream_detail_maps_metadata() -> None:
    detail = {
        "answer": "Antwoord",
        "citations": [{"celex": "32024R1689", "excerpt": "AI Act", "trust": {}}],
        "retrieval_route": "local",
        "confidence_score": 0.82,
        "verification_questions": ["Welke situatie geldt?"],
        "coverage_status": "adequate",
        "coverage_guidance": None,
    }
    response = answer_from_stream_detail(detail, "conv-1", "layperson", "nl")
    assert response.confidence_score == 0.82
    assert response.verification_questions == ["Welke situatie geldt?"]
    assert response.coverage_status == "adequate"
    assert response.citations[0].celex == "32024R1689"
