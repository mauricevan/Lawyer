"""Orchestrate chunk-grounded layperson answers — no template fill."""
from typing import Any

from backend.src.services.layperson_grounded_answer_service import LaypersonGroundedAnswerService


class LaypersonClearAnswerComposer:
    """Build layperson markdown from EUR-Lex chunks only."""

    def __init__(self) -> None:
        self._grounded = LaypersonGroundedAnswerService()

    async def compose(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        return await self._grounded.compose(question, chunks)

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
        return self._grounded.compose_extractive(question, chunks)
