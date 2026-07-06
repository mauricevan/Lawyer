"""Agentic EUR-Lex research — live fetch, in-document search, grounded chunks."""
import asyncio
import logging
from typing import Any

from backend.src.config import settings
from backend.src.security.ssrf_guard import SecurityValidationError, validate_celex
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.eurlex_document_session_service import EurlexDocumentSessionService
from backend.src.utils.eurlex_query_terms import build_query_terms
from backend.src.utils.chunk_metadata_normalizer import normalize_retrieval_chunks
from backend.src.utils.eurlex_research_chunk_adapter import hits_to_retrieval_chunks
from backend.src.utils.in_document_search import search_articles_in_document
from ingestion.src.clients.sparql_client import SparqlClient
from shared.schemas.legal_interpretation import AgentFetchResult, InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

logger = logging.getLogger(__name__)


class EurlexResearchService:
    """Discover CELEX acts, load full documents, search articles in-document."""

    def __init__(self) -> None:
        self._sessions = EurlexDocumentSessionService()
        self._quality = ChunkQualityService()
        self._sparql = SparqlClient(timeout=settings.live_fallback_timeout_seconds)

    async def fetch(
        self,
        plan: LegalInterpretationPlan,
        request: QueryRequest,
    ) -> AgentFetchResult:
        """Build AgentFetchResult from live EUR-Lex research only (no Qdrant truth)."""
        celex_targets = self._resolve_targets(plan, request.question)
        if not celex_targets:
            return AgentFetchResult(chunks=[], fetch_ok=False, fetch_source="eurlex_research")
        terms = build_query_terms(request.question, tuple(plan.search_keywords))
        tasks = [
            self._research_instrument(target, terms, request.language)
            for target in celex_targets[: settings.agent_max_instruments]
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        merged: list[dict[str, Any]] = []
        attempted: list[str] = []
        for target, result in zip(celex_targets, results):
            attempted.append(target.celex or target.name)
            if isinstance(result, Exception):
                logger.warning("eurlex_research_failed celex=%s err=%s", target.celex, result)
                continue
            merged.extend(result)
        merged = self._dedupe_chunks(merged)[: settings.agent_research_max_articles]
        merged = self._quality.filter_chunks(merged, expected_language=request.language)
        merged = normalize_retrieval_chunks(merged)
        fetch_ok = bool(merged)
        return AgentFetchResult(
            chunks=merged,
            fetch_ok=fetch_ok,
            fetch_source="eurlex_research",
            attempted_celex=attempted,
            resolved_celex=[t.celex for t in celex_targets if t.celex],
            articles_fetched=_article_numbers(merged),
            fetch_attempted=True,
        )

    async def _research_instrument(
        self,
        instrument: InstrumentTarget,
        terms: tuple[str, ...],
        language: str,
    ) -> list[dict[str, Any]]:
        if not instrument.celex:
            return []
        try:
            celex = validate_celex(instrument.celex)
        except SecurityValidationError:
            return []
        session = await self._sessions.load(celex, language)
        if not session:
            return []
        hints = tuple(instrument.articles[: settings.agent_max_articles_per_instrument])
        if hints:
            hits = search_articles_in_document(
                session,
                (),
                article_hints=hints,
                limit=len(hints),
            )
        else:
            hits = search_articles_in_document(
                session,
                terms,
                article_hints=None,
                limit=settings.agent_research_max_articles,
            )
        chunks = hits_to_retrieval_chunks(hits)
        for chunk in chunks:
            chunk["language"] = session.language
            chunk["title"] = session.title
        return chunks

    def _resolve_targets(
        self,
        plan: LegalInterpretationPlan,
        question: str,
    ) -> list[InstrumentTarget]:
        if plan.instruments:
            return [inst for inst in plan.instruments if inst.celex]
        discovered = self._extract_celex(question)
        if discovered:
            return [InstrumentTarget(name=discovered, celex=discovered, articles=())]
        return []

    def _extract_celex(self, question: str) -> str | None:
        import re

        match = re.search(r"\b(\d{5}[A-Z]\d{4})\b", question.upper())
        return match.group(1) if match else None

    async def discover_celex(self, question: str, language: str = "nl") -> str | None:
        """SPARQL discovery for any EUR-Lex legislation title match."""
        try:
            candidates = await self._sparql.discover_celex_candidates(question, language, limit=3)
            if candidates:
                return candidates[0].get("celex") or None
        except Exception as exc:
            logger.warning("eurlex_discover_failed: %s", exc)
        return None

    @staticmethod
    def _dedupe_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for chunk in chunks:
            key = f"{chunk.get('celex')}:{chunk.get('article_number')}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(chunk)
        return unique


def _article_numbers(chunks: list[dict[str, Any]]) -> list[str]:
    numbers = [str(c.get("article_number")) for c in chunks if c.get("article_number")]
    return sorted(set(numbers), key=lambda n: int(n) if n.isdigit() else n)
