"""Grounded layperson answers from EUR-Lex chunks only (plan.md §E)."""
import logging
from typing import Any

from backend.src.utils.article_chunk_filter import drop_unbound_article_references
from backend.src.utils.layperson_answer_formatter import is_weak_layperson_answer
from backend.src.utils.layperson_grounded_context import build_grounded_context
from backend.src.utils.layperson_grounded_extractive import build_grounded_extractive_answer
from backend.src.utils.layperson_grounded_official import render_official_text_from_chunks
from backend.src.utils.llm_json_client import call_llm_text
from backend.src.utils.retrieval_substance import has_substantive_retrieval
from shared.config.prompt_loader import (
    get_layperson_grounded_answer_system,
    get_layperson_grounded_answer_user_template,
)

logger = logging.getLogger(__name__)
_MIN_ANSWER_CHARS = 200


class LaypersonGroundedAnswerService:
    """Compose layperson answers grounded in retrieval chunks."""

    async def compose(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        """Try LLM prose from chunks; fall back to extractive or planner-framed answer."""
        extractive = build_grounded_extractive_answer(question, chunks)
        if extractive and not has_substantive_retrieval(chunks):
            return extractive
        if not has_substantive_retrieval(chunks):
            return None
        llm_text = await self._try_llm_answer(question, chunks)
        if llm_text:
            return llm_text
        return extractive or build_grounded_extractive_answer(question, chunks)

    def compose_extractive(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        """Build extractive answer without LLM."""
        return build_grounded_extractive_answer(question, chunks)

    async def _try_llm_answer(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        context = build_grounded_context(chunks)
        if not context:
            return None
        try:
            user = get_layperson_grounded_answer_user_template().format(
                question=question,
                context=context,
            )
            raw = await call_llm_text(
                get_layperson_grounded_answer_system(),
                user,
                max_tokens=1200,
            )
        except Exception as exc:
            logger.warning("Grounded layperson LLM failed: %s", exc)
            return None
        return self._finalize_llm_text(raw.strip(), chunks)

    def _finalize_llm_text(self, text: str, chunks: list[dict[str, Any]]) -> str | None:
        if len(text) < _MIN_ANSWER_CHARS:
            return None
        filtered = drop_unbound_article_references(text, chunks)
        if is_weak_layperson_answer(filtered):
            return None
        return self._append_official_if_missing(filtered, chunks)

    def _append_official_if_missing(self, text: str, chunks: list[dict[str, Any]]) -> str:
        if "## Officiële tekst" in text:
            return text
        from backend.src.utils.article_chunk_filter import retrieved_article_numbers

        official = render_official_text_from_chunks(
            chunks,
            articles=retrieved_article_numbers(chunks),
        )
        if not official:
            return text
        let_op = "## Let op"
        if let_op in text:
            return text.replace(let_op, f"{official}\n\n{let_op}", 1)
        return f"{text.rstrip()}\n\n{official}"
