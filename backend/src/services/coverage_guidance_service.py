"""Resolve topic-specific guidance for coverage-gap answers."""
from shared.config.coverage_guidance_loader import (
    get_coverage_topics,
    topic_to_guidance,
)
from shared.schemas.coverage_guidance import CoverageGuidance


class CoverageGuidanceService:
    """Maps user questions to configured guidance topics."""

    def resolve(self, question: str) -> CoverageGuidance:
        topic = self._match_topic(question)
        return topic_to_guidance(topic)

    def _match_topic(self, question: str) -> dict:
        lowered = question.lower()
        fallback = self._fallback_topic()
        for topic in get_coverage_topics():
            if topic.get("id") == "fallback_general":
                continue
            patterns = topic.get("patterns", [])
            if any(str(p).lower() in lowered for p in patterns):
                return topic
        return fallback

    def _fallback_topic(self) -> dict:
        for topic in get_coverage_topics():
            if topic.get("id") == "fallback_general":
                return topic
        return {
            "id": "fallback_general",
            "sensitivity": "low",
            "empathy_opener": "",
            "frameworks": [],
            "referrals": [],
        }
