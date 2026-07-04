"""Orchestrate live/cache article fetch for agent flow."""
import asyncio
import logging
from typing import Any

from backend.src.config import settings
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.live_retrieval_service import LiveRetrievalService
from backend.src.services.qdrant_service import QdrantService
from backend.src.utils.article_chunk_filter import filter_chunks_by_articles_strict
from backend.src.utils.legal_domain_retrieval_filter import (
    filter_chunks_by_domain,
    rank_chunks_by_domain,
)
from backend.src.utils.legal_question_type_chunk_scoring import rank_chunks_by_question_type
from shared.schemas.legal_interpretation import AgentFetchResult, InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

logger = logging.getLogger(__name__)


class ArticleFetchOrchestratorService:
    """Fetch article chunks per resolved instrument with cache-first strategy."""

    def __init__(self) -> None:
        self._live = LiveRetrievalService()
        self._qdrant = QdrantService()
        self._quality = ChunkQualityService()

    async def fetch(
        self,
        plan: LegalInterpretationPlan,
        request: QueryRequest,
        session: Any | None = None,
    ) -> AgentFetchResult:
        if not plan.instruments:
            return AgentFetchResult(chunks=[], fetch_ok=False, fetch_source="live")
        instruments = plan.instruments[: settings.agent_max_instruments]
        tasks = [self._fetch_instrument(inst, plan, request) for inst in instruments]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        merged: list[dict[str, Any]] = []
        sources: list[str] = []
        attempted: list[str] = []
        fetch_ok = False
        for inst, result in zip(instruments, results):
            attempted.append(inst.celex or inst.name)
            if isinstance(result, Exception):
                logger.warning("Instrument fetch failed %s: %s", inst.celex, result)
                continue
            chunks, source = result
            if chunks:
                fetch_ok = True
                merged.extend(chunks)
                sources.append(source)
        merged = _dedupe_chunks(merged)[: settings.agent_max_total_chunks]
        merged = self._quality.filter_chunks(merged, expected_language=request.language)
        merged = filter_chunks_by_domain(merged, plan.legal_domain)
        merged = rank_chunks_by_domain(merged, plan.legal_domain)
        merged = rank_chunks_by_question_type(merged, plan.legal_question_type)
        fetch_source = sources[0] if sources else "live"
        if len(set(sources)) > 1:
            fetch_source = "mixed"
        return AgentFetchResult(
            chunks=merged,
            fetch_ok=fetch_ok,
            fetch_source=fetch_source,
            attempted_celex=attempted,
            resolved_celex=[i.celex for i in instruments if i.celex],
            articles_fetched=_article_numbers(merged),
            fetch_attempted=bool(attempted),
        )

    async def _fetch_instrument(
        self,
        instrument: InstrumentTarget,
        plan: LegalInterpretationPlan,
        request: QueryRequest,
    ) -> tuple[list[dict[str, Any]], str]:
        if not instrument.celex:
            return [], "none"
        articles = tuple(instrument.articles[: settings.agent_max_articles_per_instrument])
        cached = self._cache_chunks(instrument.celex, articles, request.language)
        if cached:
            return cached, "cache"
        keywords = tuple(plan.search_keywords)
        chunks = await self._live.fallback_chunks(
            request.question,
            language=request.language,
            celex_hint=instrument.celex,
            article_hints=articles or None,
            strict_articles=bool(articles),
            search_keywords=keywords or None,
            agent_mode=True,
        )
        return chunks, "live"

    def _cache_chunks(
        self,
        celex: str,
        articles: tuple[str, ...],
        language: str,
    ) -> list[dict[str, Any]]:
        try:
            hits = self._qdrant.search_by_celex(
                {celex},
                limit=settings.agent_max_total_chunks,
                language=language,
            )
            if articles:
                hits = filter_chunks_by_articles_strict(hits, articles)
            hits = self._quality.filter_chunks(hits, expected_language=language)
            return hits if hits else []
        except Exception as exc:
            logger.debug("Cache lookup failed for %s: %s", celex, exc)
            return []


def _dedupe_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for chunk in chunks:
        key = chunk.get("chunk_id") or f"{chunk.get('celex')}:{chunk.get('article_number')}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(chunk)
    return unique


def _article_numbers(chunks: list[dict[str, Any]]) -> list[str]:
    numbers = [str(c.get("article_number")) for c in chunks if c.get("article_number")]
    return sorted(set(numbers), key=lambda n: int(n) if n.isdigit() else n)
