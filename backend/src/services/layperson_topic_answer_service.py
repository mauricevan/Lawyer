"""Deterministic layperson answers for known EU topics."""
from backend.src.services.layperson_topic_service import LaypersonTopicMatch
from backend.src.utils.layperson_clear_markdown import render_clear_answer
from backend.src.utils.layperson_topic_clear_mapper import topic_match_to_clear_answer


class LaypersonTopicAnswerService:
    """Builds structured markdown for matched layperson topics."""

    def build(self, match: LaypersonTopicMatch, audience: str = "layperson") -> str:
        if audience == "professional":
            return self._build_professional(match)
        return render_clear_answer(topic_match_to_clear_answer(match))

    def _build_professional(self, match: LaypersonTopicMatch) -> str:
        return (
            f"{match.short_answer_nl}\n\n{match.summary_nl}\n\n"
            f"**Kader:** {match.regulation_title}\n\n"
            f"**Let op:** Dit is geen persoonlijk juridisch advies."
        )
