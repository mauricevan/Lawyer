"""Compose structured layperson answers from answer frame + chunks + obligation templates."""
from typing import Any

from backend.src.services.layperson_answer_frame_service import LaypersonAnswerFrame
from backend.src.services.legal_planner_template_loader import resolve_obligation_templates
from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.article_chunk_filter import (
    chunks_include_planned_articles,
    drop_unbound_article_references,
    is_article_in_chunks,
)
from backend.src.utils.declarant_uncertainties import render_uncertainties_section
from backend.src.utils.layperson_grounded_official import render_official_text_from_chunks
from backend.src.utils.layperson_prose_builder import _extract_sentences, _join_sentences
from backend.src.utils.legal_chunk_text import clean_chunk_text

_DEFAULT_LET_OP = (
    "Dit is algemene informatie, geen persoonlijk juridisch advies. "
    "Raadpleeg een jurist bij twijfel over uw situatie."
)


def compose_synoptic_layperson_answer(
    question: str,
    chunks: list[dict[str, Any]],
    frame: LaypersonAnswerFrame,
) -> str | None:
    """Build markdown with synoptic kort antwoord and plan-aligned sections."""
    templates = resolve_obligation_templates(
        frame.plan_id or "",
        frame.celex or "",
        _domain_for_plan(frame.plan_id),
    )
    if not templates and not chunks:
        return None
    grounded_chunks = (
        chunks
        if chunks_include_planned_articles(chunks, frame.articles)
        else []
    )
    kort = _build_kort(frame, grounded_chunks, templates)
    law_says = _build_law_says(frame, grounded_chunks, templates)
    practical = _build_practical(frame, templates, grounded_chunks)
    if not kort or not law_says:
        return None
    sections = [
        f"## Kort antwoord\n{kort}",
        f"## Wat de EU-regels zeggen\n{law_says}",
        practical,
    ]
    official = render_official_text_from_chunks(
        chunks,
        articles=_article_set(frame, templates, grounded_chunks, include_retrieved=False),
    )
    if official:
        sections.append(official)
    uncertainties = render_uncertainties_section(question)
    if uncertainties:
        sections.append(uncertainties)
    sections.append(f"## Let op\n{_DEFAULT_LET_OP}")
    allowed = tuple(_article_set(frame, templates, chunks))
    return drop_unbound_article_references("\n\n".join(sections), chunks, allowed_articles=allowed)


def _build_kort(
    frame: LaypersonAnswerFrame,
    chunks: list[dict[str, Any]],
    templates: list[dict[str, str]],
) -> str | None:
    support = _supporting_sentence(frame, chunks, templates)
    if support:
        return f"{frame.synoptic_lead}\n\n{support}"
    return frame.synoptic_lead


def _supporting_sentence(
    frame: LaypersonAnswerFrame,
    chunks: list[dict[str, Any]],
    templates: list[dict[str, str]],
) -> str | None:
    for article in frame.articles:
        text = _chunk_text_for_article(chunks, article)
        if not text:
            continue
        sentences = _extract_sentences(text, max_count=4)
        if sentences:
            reg = regulation_label(frame.celex or "")
            return f"**Artikel {article}** ({reg}): {_join_sentences(sentences[:1], max_len=280)}"
    for template in templates[:2]:
        article = str(template.get("article", "")).strip()
        text = _chunk_text_for_article(chunks, article)
        if not text:
            continue
        sentences = _extract_sentences(text, max_count=4)
        if sentences:
            reg = regulation_label(frame.celex or "")
            return f"**Artikel {article}** ({reg}): {_join_sentences(sentences[:1], max_len=280)}"
    return None


def _build_law_says(
    frame: LaypersonAnswerFrame,
    chunks: list[dict[str, Any]],
    templates: list[dict[str, str]],
) -> str | None:
    blocks: list[str] = []
    reg = regulation_label(frame.celex or "")
    for template in templates[:4]:
        article = str(template.get("article", "")).strip()
        if not article:
            continue
        body = _chunk_text_for_article(chunks, article)
        excerpt = _join_sentences(_extract_sentences(body, max_count=4), max_len=700) if body else ""
        uitleg = str(template.get("uitleg", "")).strip()
        if excerpt:
            blocks.append(f"**Artikel {article}** ({reg})\n\n{excerpt}")
        elif uitleg:
            blocks.append(
                f"**Artikel {article}** ({reg})\n\n{template.get('title', template.get('label', ''))}: {uitleg}"
            )
    if blocks:
        return "\n\n".join(blocks)
    return _fallback_law_from_chunks(chunks, reg)


def _fallback_law_from_chunks(chunks: list[dict[str, Any]], reg: str) -> str | None:
    blocks: list[str] = []
    for chunk in chunks[:3]:
        article = str(chunk.get("article_number", "")).strip()
        if not article:
            continue
        text = clean_chunk_text(str(chunk.get("text", "")))
        body = _join_sentences(_extract_sentences(text, max_count=4), max_len=700)
        if body:
            blocks.append(f"**Artikel {article}** ({reg})\n\n{body}")
    return "\n\n".join(blocks) if blocks else None


def _build_practical(
    frame: LaypersonAnswerFrame,
    templates: list[dict[str, str]],
    chunks: list[dict[str, Any]],
) -> str:
    lines = ["## Wat dit in de praktijk betekent", ""]
    for template in templates[:4]:
        label = str(template.get("label", "")).strip()
        article = str(template.get("article", "")).strip()
        uitleg = str(template.get("uitleg", "")).strip()
        if not uitleg:
            continue
        prefix = f"Art. {article}" if article else label
        lines.append(f"- **{prefix}:** {uitleg}")
    if len(lines) <= 2:
        for chunk in chunks[:2]:
            article = str(chunk.get("article_number", "")).strip()
            if article and is_article_in_chunks(article, chunks):
                lines.append(f"- **Artikel {article}:** Zie de EU-tekst hierboven voor uw concrete plichten.")
    if len(lines) <= 2:
        lines.append("- **Kernregel:** Raadpleeg de EU-bronnen hierboven en een jurist voor uw situatie.")
    return "\n".join(lines)


def _chunk_text_for_article(chunks: list[dict[str, Any]], article: str) -> str:
    if not article:
        return ""
    norm = article.lstrip("0") or article
    for chunk in chunks:
        num = str(chunk.get("article_number", "")).strip()
        if num.lstrip("0") == norm or num == article:
            return clean_chunk_text(str(chunk.get("text", "")))
    return ""


def _article_set(
    frame: LaypersonAnswerFrame,
    templates: list[dict[str, str]],
    chunks: list[dict[str, Any]],
    *,
    include_retrieved: bool = True,
) -> set[str]:
    articles = {str(a) for a in frame.articles if a}
    articles.update(str(t.get("article", "")).strip() for t in templates if t.get("article"))
    if include_retrieved:
        for chunk in chunks:
            num = str(chunk.get("article_number", "")).strip()
            if num:
                articles.add(num)
    return {a for a in articles if a}


def _domain_for_plan(plan_id: str | None) -> str | None:
    mapping = {
        "gdpr_lawful_basis": "privacy",
        "gdpr_marketing_sharing": "privacy",
        "gpsr_manufacturer_risk": "consumer",
        "consumer_withdrawal": "consumer",
    }
    return mapping.get(plan_id or "")
