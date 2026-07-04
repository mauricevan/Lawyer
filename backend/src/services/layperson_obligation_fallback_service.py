"""Rule-based layperson answers from planner obligation templates (no LLM)."""
from typing import Any

from backend.src.services.legal_extractive_generic import collect_generic_excerpts
from backend.src.services.legal_planner_template_loader import resolve_obligation_templates
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.layperson_clear_markdown import render_clear_answer
from backend.src.utils.layperson_generic_prose import build_kort_antwoord, build_let_op, build_voorbeeld
from backend.src.utils.legal_chunk_text import clean_chunk_text
from shared.schemas.layperson_clear_answer import (
    ArticleSummary,
    LaypersonClearAnswer,
    ObligationRow,
    OfficialExcerpt,
)


class LaypersonObligationFallbackService:
    """Build clear layperson answers from planner templates + optional NL chunks."""

    def compose(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        plan = LegalSourcePlannerService().plan(question)
        if not plan:
            return None
        templates = resolve_obligation_templates(plan.plan_id, plan.celex, plan.legal_domain)
        if not templates and not plan.articles:
            return None
        excerpts = collect_generic_excerpts(chunks, question, limit=5)
        if not excerpts and not templates:
            return None
        reg_label = regulation_label(plan.celex)
        answer = self._build_answer(question, plan, templates, excerpts, reg_label, chunks)
        if not answer.kort_antwoord or len(answer.obligations) < 2:
            return None
        if not answer.voorbeeld.strip():
            return None
        return render_clear_answer(answer)

    def _build_answer(
        self,
        question: str,
        plan: Any,
        templates: list[dict[str, str]],
        excerpts: list[dict[str, str]],
        reg_label: str,
        chunks: list[dict[str, Any]],
    ) -> LaypersonClearAnswer:
        by_article = {str(e.get("article", "")): e for e in excerpts}
        obligations: list[ObligationRow] = []
        basis: list[ArticleSummary] = []
        for template in templates:
            article = str(template.get("article", ""))
            label = str(template.get("label", ""))
            default_uitleg = str(template.get("uitleg", ""))
            excerpt = by_article.get(article) or by_article.get(article.lstrip("0"))
            uitleg = default_uitleg or _plain_summary(excerpt.get("text", "") if excerpt else "")
            if not uitleg:
                continue
            obligations.append(ObligationRow(label=label, uitleg=uitleg[:280]))
            basis.append(ArticleSummary(
                article=article,
                title=str(template.get("title", "")),
                uitleg_nl=uitleg[:320],
            ))
        return LaypersonClearAnswer(
            kort_antwoord=build_kort_antwoord(question, reg_label, obligations),
            obligations=obligations,
            voorbeeld=build_voorbeeld(question, obligations),
            juridische_basis=basis,
            begrippen=[],
            let_op=build_let_op(),
            official_excerpts=_official_excerpts(chunks, plan.articles),
        )


def _plain_summary(text: str) -> str:
    cleaned = clean_chunk_text(text)
    if len(cleaned) < 80:
        return ""
    sentence = cleaned.split(". ")[0].strip()
    if len(sentence) > 220:
        return sentence[:217] + "…"
    return sentence + ("." if not sentence.endswith(".") else "")


def _official_excerpts(chunks: list[dict[str, Any]], articles: tuple[str, ...]) -> list[OfficialExcerpt]:
    wanted = {a.lstrip("0") for a in articles}
    excerpts: list[OfficialExcerpt] = []
    for chunk in chunks:
        article = str(chunk.get("article_number") or "")
        if article.lstrip("0") not in wanted:
            continue
        text = clean_chunk_text(str(chunk.get("text", "")))
        if len(text) < 80:
            continue
        excerpts.append(OfficialExcerpt(
            article=article,
            label=f"Artikel {article}",
            text=text[:600] + ("…" if len(text) > 600 else ""),
        ))
        if len(excerpts) >= 3:
            break
    return excerpts
