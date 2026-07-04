"""Orchestrate antwoord-eerst layperson answers — one generic pipeline for all questions."""
from typing import Any

from backend.src.services.layperson_obligation_fallback_service import LaypersonObligationFallbackService
from backend.src.services.layperson_synthesis_service import LaypersonSynthesisService
from backend.src.services.legal_extractive_generic import build_generic_layperson, can_build_generic_answer


class LaypersonClearAnswerComposer:
    """Build layperson markdown: synthesis → planner templates → extractive fallback."""

    def __init__(self) -> None:
        self._synthesis = LaypersonSynthesisService()
        self._fallback = LaypersonObligationFallbackService()

    async def compose(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        synthesized = await self._synthesis.compose(question, chunks)
        if synthesized:
            return synthesized
        return self.compose_without_llm(question, chunks)

    def compose_without_llm(
        self,
        question: str,
        chunks: list[dict[str, Any]],
        *,
        allow_topic: bool = False,
    ) -> str | None:
        if allow_topic:
            from backend.src.services.layperson_topic_service import LaypersonTopicService
            from backend.src.utils.layperson_clear_markdown import render_clear_answer
            from backend.src.utils.layperson_topic_clear_mapper import topic_match_to_clear_answer

            topic = LaypersonTopicService().match(question)
            if topic:
                return render_clear_answer(topic_match_to_clear_answer(topic))
        template_answer = self._fallback.compose(question, chunks)
        if template_answer:
            return template_answer
        if not can_build_generic_answer(chunks, question):
            return None
        return build_generic_layperson(question, chunks)
