"""Deterministic layperson answers for known EU topics."""
from backend.src.services.layperson_topic_service import LaypersonTopicMatch

_LEGAL_NOTICE = (
    "Dit is geen persoonlijk juridisch advies. Raadpleeg een jurist of de genoemde "
    "instantie voor uw specifieke situatie."
)


class LaypersonTopicAnswerService:
    """Builds structured markdown for matched layperson topics."""

    def build(self, match: LaypersonTopicMatch, audience: str = "layperson") -> str:
        if audience == "professional":
            return self._build_professional(match)
        return self._build_layperson(match)

    def _build_layperson(self, match: LaypersonTopicMatch) -> str:
        sections = [f"## Kort antwoord\n{match.short_answer_nl}"]
        sections.append(f"## Uitleg\n{match.summary_nl}")
        sections.append(f"## Wat dit voor u kan betekenen\n{match.practical_nl}")
        sections.append(f"## Let op\n{_LEGAL_NOTICE}")
        return "\n\n".join(sections)

    def _build_professional(self, match: LaypersonTopicMatch) -> str:
        return (
            f"{match.short_answer_nl}\n\n{match.summary_nl}\n\n"
            f"**Kader:** {match.regulation_title}\n\n**Let op:** {_LEGAL_NOTICE}"
        )
