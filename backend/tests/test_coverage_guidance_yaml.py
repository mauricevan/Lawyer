"""Validate coverage_guidance.yaml against Pydantic schemas."""
from shared.config.coverage_guidance_loader import get_coverage_topics, topic_to_guidance


def test_all_topic_sensitivities_are_valid() -> None:
    for topic in get_coverage_topics():
        guidance = topic_to_guidance(topic)
        assert guidance.sensitivity in {"low", "high"}
        assert guidance.topic_id == topic["id"]


def test_national_law_topic_is_high_sensitivity() -> None:
    topics = {t["id"]: t for t in get_coverage_topics()}
    guidance = topic_to_guidance(topics["national_law"])
    assert guidance.sensitivity == "high"
