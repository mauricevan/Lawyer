"""LLM synthesis of structured layperson answers from NL legal chunks."""
import logging
from typing import Any

from backend.src.utils.layperson_clear_markdown import render_clear_answer
from backend.src.utils.legal_chunk_text import clean_chunk_text
from backend.src.utils.layperson_synthesis_context import (
    build_synthesis_context,
    build_synthesis_hints,
)
from backend.src.utils.llm_json_client import call_llm_json
from shared.config.prompt_loader import get_layperson_synthesis_system, get_layperson_synthesis_user_template
from shared.schemas.layperson_clear_answer import (
    ArticleSummary,
    LaypersonClearAnswer,
    ObligationRow,
    OfficialExcerpt,
    TermDefinition,
)

logger = logging.getLogger(__name__)


class LaypersonSynthesisService:
    """Synthesize LaypersonClearAnswer JSON from question + chunks or planner templates."""

    async def compose(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        context = build_synthesis_context(question, chunks)
        if not context:
            return None
        try:
            raw = await self._call_synthesis(question, context)
            answer = _parse_synthesis(raw, chunks)
            if not _is_complete_answer(answer):
                return None
            return render_clear_answer(answer)
        except Exception as exc:
            logger.warning("Layperson synthesis failed: %s", exc)
            return None

    async def _call_synthesis(self, question: str, context: str) -> dict:
        user = get_layperson_synthesis_user_template().format(
            question=question,
            context=context,
            interpretation_hints=build_synthesis_hints(question),
        )
        return await call_llm_json(get_layperson_synthesis_system(), user, max_tokens=1200)

    def build_from_dict(self, raw: dict, chunks: list[dict[str, Any]]) -> LaypersonClearAnswer:
        return _parse_synthesis(raw, chunks)


def _is_complete_answer(answer: LaypersonClearAnswer) -> bool:
    return bool(
        answer.kort_antwoord
        and len(answer.obligations) >= 2
        and answer.voorbeeld.strip()
        and answer.juridische_basis
    )


def _parse_synthesis(raw: dict, chunks: list[dict[str, Any]]) -> LaypersonClearAnswer:
    obligations = [
        ObligationRow(label=str(row.get("label", "")), uitleg=str(row.get("uitleg", "")))
        for row in raw.get("obligations", [])
        if row.get("label") and row.get("uitleg")
    ]
    basis = [
        ArticleSummary(
            article=str(row.get("article", "")),
            title=str(row.get("title", "")),
            uitleg_nl=str(row.get("uitleg_nl", "")),
        )
        for row in raw.get("juridische_basis", [])
        if row.get("article") and row.get("uitleg_nl")
    ]
    terms = [
        TermDefinition(term=str(row.get("term", "")), definition_nl=str(row.get("definition_nl", "")))
        for row in raw.get("begrippen", [])
        if row.get("term") and row.get("definition_nl")
    ]
    excerpts = _official_from_chunks(chunks) if not raw.get("official_excerpts") else [
        OfficialExcerpt(
            article=str(row.get("article", "")),
            label=str(row.get("label", "")),
            text=str(row.get("text", "")),
        )
        for row in raw.get("official_excerpts", [])
        if row.get("text")
    ]
    return LaypersonClearAnswer(
        kort_antwoord=str(raw.get("kort_antwoord", "")).strip(),
        obligations=obligations,
        voorbeeld=str(raw.get("voorbeeld", "")).strip(),
        juridische_basis=basis,
        begrippen=terms,
        let_op=str(raw.get("let_op", "")).strip(),
        official_excerpts=excerpts or _official_from_chunks(chunks),
    )


def _official_from_chunks(chunks: list[dict[str, Any]]) -> list[OfficialExcerpt]:
    excerpts: list[OfficialExcerpt] = []
    for chunk in chunks[:3]:
        text = clean_chunk_text(str(chunk.get("text", "")))
        if len(text) < 80:
            continue
        article = str(chunk.get("article_number") or "")
        excerpts.append(OfficialExcerpt(
            article=article,
            label=f"Artikel {article}" if article else "Bron",
            text=text[:600] + ("…" if len(text) > 600 else ""),
        ))
    return excerpts
