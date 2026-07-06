"""Chunk-grounded extractive layperson answers (plan.md §E fallback)."""
from typing import Any

from backend.src.services.layperson_answer_frame_service import resolve_layperson_answer_frame
from backend.src.utils.declarant_uncertainties import render_uncertainties_section
from backend.src.services.legal_extractive_generic import collect_generic_excerpts
from backend.src.utils.article_chunk_filter import drop_unbound_article_references, is_article_in_chunks
from backend.src.utils.layperson_grounded_official import render_official_text_from_chunks
from backend.src.utils.layperson_prose_builder import _build_kort_antwoord, _build_uitleg, _extract_sentences
from backend.src.utils.layperson_synoptic_composer import compose_synoptic_layperson_answer
from backend.src.utils.retrieval_substance import has_substantive_retrieval

_DEFAULT_LET_OP = (
    "Dit is algemene informatie, geen persoonlijk juridisch advies. "
    "Raadpleeg een jurist bij twijfel over uw situatie."
)


def build_grounded_extractive_answer(
    question: str,
    chunks: list[dict[str, Any]],
) -> str | None:
    """Build markdown answer using retrieved article text or planner templates."""
    frame = resolve_layperson_answer_frame(question)
    if frame:
        synoptic = compose_synoptic_layperson_answer(question, chunks, frame)
        if synoptic:
            return synoptic
    if not has_substantive_retrieval(chunks):
        return None
    excerpts = _bound_excerpts(chunks, question)
    if not excerpts:
        return None
    kort = _build_kort_antwoord(question, excerpts)
    law_says = _build_uitleg(excerpts, question)
    if not kort or not law_says:
        return None
    practical = _build_practical_bullets(excerpts)
    article_set = {str(item.get("article", "")).strip() for item in excerpts if item.get("article")}
    official = render_official_text_from_chunks(chunks, articles=article_set)
    sections = [
        f"## Kort antwoord\n{kort}",
        f"## Wat de EU-regels zeggen\n{law_says}",
        practical,
    ]
    if official:
        sections.append(official)
    uncertainties = render_uncertainties_section(question)
    if uncertainties:
        sections.append(uncertainties)
    sections.append(f"## Let op\n{_DEFAULT_LET_OP}")
    answer = "\n\n".join(sections)
    return drop_unbound_article_references(answer, chunks)


def _bound_excerpts(
    chunks: list[dict[str, Any]],
    question: str,
) -> list[dict[str, str]]:
    excerpts: list[dict[str, str]] = []
    for item in collect_generic_excerpts(chunks, question, limit=4):
        article = str(item.get("article", "")).strip()
        if article and is_article_in_chunks(article, chunks):
            excerpts.append(item)
    return excerpts


def _build_practical_bullets(excerpts: list[dict[str, str]]) -> str:
    lines = ["## Wat dit in de praktijk betekent", ""]
    for item in excerpts[:3]:
        article = str(item.get("article", "")).strip()
        sentences = _extract_sentences(str(item.get("text", "")), max_count=2)
        for sentence in sentences:
            label = _bullet_label(sentence, article)
            lines.append(f"- **{label}:** {sentence}")
    if len(lines) <= 2:
        lines.append("- **Kernregel:** Zie de EU-regels hierboven voor uw concrete plichten.")
    return "\n".join(lines)


def _bullet_label(sentence: str, article: str) -> str:
    lowered = sentence.lower()
    if "melden" in lowered or "kennis" in lowered:
        return f"Melden (art. {article})" if article else "Melden"
    if "herstel" in lowered or "maatregel" in lowered:
        return f"Maatregelen (art. {article})" if article else "Maatregelen"
    if "verplicht" in lowered or "moet" in lowered:
        return f"Verplichting (art. {article})" if article else "Verplichting"
    return f"Artikel {article}" if article else "Kernregel"
