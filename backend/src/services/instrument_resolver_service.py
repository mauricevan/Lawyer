"""Resolve instrument targets to confirmed CELEX identifiers."""
import logging
import re

from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.legal_domain_retrieval_filter import (
    default_instrument_for_domain,
    filter_instruments_by_domain,
    is_celex_allowed_for_domain,
)
from ingestion.src.clients.sparql_client import SparqlClient
from ingestion.src.data.oj_citation_parser import parse_oj_celex
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan

logger = logging.getLogger(__name__)
_EXPLICIT_CELEX = re.compile(r"\b(\d{5}[A-Z]\d{4})\b")


class InstrumentResolverService:
    """Fill CELEX on interpretation plan instruments."""

    def __init__(self) -> None:
        self._discovery = CelexDiscoveryService()
        self._sparql = SparqlClient()

    async def resolve(
        self,
        plan: LegalInterpretationPlan,
        question: str,
        language: str = "nl",
        retrieval_query: str | None = None,
    ) -> LegalInterpretationPlan:
        if plan.is_national_law:
            return plan
        search_text = retrieval_query or question
        resolved: list[InstrumentTarget] = []
        for instrument in plan.instruments:
            item = await self._resolve_one(instrument, search_text, language, plan)
            if item.celex:
                resolved.append(item)
        if not resolved:
            resolved = await self._resolve_from_question(search_text, language, plan)
        resolved = _merge_rule_plan_articles(question, resolved)
        resolved = filter_instruments_by_domain(resolved, plan.legal_domain)
        if not resolved and plan.legal_domain != "unknown":
            fallback = default_instrument_for_domain(plan.legal_domain, search_text)
            if fallback:
                resolved = [fallback]
        return plan.model_copy(update={"instruments": resolved[:3]})

    async def _resolve_one(
        self,
        instrument: InstrumentTarget,
        search_text: str,
        language: str,
        plan: LegalInterpretationPlan,
    ) -> InstrumentTarget:
        celex = instrument.celex
        title = instrument.title
        if not celex:
            celex = _explicit_celex(search_text) or parse_oj_celex(search_text)
        if not celex and instrument.oj_citation:
            celex = parse_oj_celex(f"Verordening {instrument.oj_citation}")
        if not celex:
            celex = await self._discover_celex(f"{instrument.name} {search_text}", language, plan)
        if celex:
            title = title or await self._fetch_title(celex, language)
        return instrument.model_copy(update={"celex": celex, "title": title})

    async def _resolve_from_question(
        self,
        question: str,
        language: str,
        plan: LegalInterpretationPlan,
    ) -> list[InstrumentTarget]:
        celex = _explicit_celex(question) or parse_oj_celex(question)
        if not celex:
            celex = await self._discover_celex(question, language, plan)
        if not celex:
            return []
        title = await self._fetch_title(celex, language)
        return [InstrumentTarget(
            name=plan.instruments[0].name if plan.instruments else (title or "EU-regelgeving"),
            celex=celex,
            articles=plan.instruments[0].articles if plan.instruments else [],
            confidence=plan.confidence,
            title=title,
        )]

    async def _discover_celex(
        self,
        text: str,
        language: str,
        plan: LegalInterpretationPlan,
    ) -> str | None:
        hits = await self._discovery.discover(text, language, limit=5)
        for hit in hits:
            if is_celex_allowed_for_domain(hit.celex, plan.legal_domain):
                return hit.celex
        return None

    async def _fetch_title(self, celex: str, language: str) -> str | None:
        try:
            meta = await self._sparql.fetch_work_by_celex(celex, language)
            return meta.get("title") if meta else None
        except Exception as exc:
            logger.warning("Title fetch failed for %s: %s", celex, exc)
            return None


def _explicit_celex(question: str) -> str | None:
    match = _EXPLICIT_CELEX.search(question.upper())
    return match.group(1) if match else None


def _merge_rule_plan_articles(
    question: str,
    instruments: list[InstrumentTarget],
) -> list[InstrumentTarget]:
    rule = LegalSourcePlannerService().plan(question)
    if not rule or not rule.articles:
        return instruments
    merged: list[InstrumentTarget] = []
    for instrument in instruments:
        if instrument.celex == rule.celex:
            articles = list(rule.articles) if not instrument.articles else list(instrument.articles)
            if rule.articles and len(rule.articles) >= len(articles):
                articles = list(rule.articles)
            merged.append(instrument.model_copy(update={"articles": articles}))
        else:
            merged.append(instrument)
    return merged
