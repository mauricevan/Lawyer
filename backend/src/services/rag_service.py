"""Hybrid RAG retrieval and answer orchestration."""
import logging
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.services.answer_policy_service import AnswerPolicyService
from backend.src.services.answer_quality_service import answer_quality_service
from backend.src.services.bm25_service import Bm25Service
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.citation_formatter import CitationFormatter
from backend.src.services.embedding_service import get_embedding_service
from backend.src.services.feature_flag_service import FeatureFlagService
from backend.src.services.live_retrieval_service import LiveRetrievalService
from backend.src.services.llm_service import LlmService
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.query_cache_service import QueryCacheService
from backend.src.services.postgres_search_service import PostgresSearchService
from backend.src.services.query_router_service import QueryRouterService
from backend.src.services.source_consistency_service import SourceConsistencyService
from backend.src.services.metrics_service import metrics_service
from backend.src.services.reranker_service import RerankerService
from backend.src.services.trust_indicator_service import TrustIndicatorService
from backend.src.utils.context_dedup import deduplicate_chunks
from backend.src.utils.qdrant_filters import doc_type_matches_celex
from backend.src.utils.retrieval_budget import RetrievalBudget, RetrievalBudgetExceeded
from ingestion.src.data.legal_term_hints import match_celex_hints
from ingestion.src.data.domain_registry_loader import get_domain_keywords
from backend.src.utils.rrf_fusion import reciprocal_rank_fusion
from shared.schemas.query import AnswerResponse, QueryFilters, QueryRequest

logger = logging.getLogger(__name__)

RETRIEVAL_CANDIDATE_LIMIT = 200
DOMAIN_KEYWORDS = get_domain_keywords()


class RagService:
    """Orchestrates hybrid search, reranking, and LLM answer generation."""

    def __init__(self) -> None:
        self._embeddings = get_embedding_service()
        self._qdrant = QdrantService()
        self._reranker = RerankerService()
        self._llm = LlmService()
        self._trust = TrustIndicatorService()
        self._citations = CitationFormatter()
        self._router = QueryRouterService()
        self._live = LiveRetrievalService()
        self._cache = QueryCacheService()
        self._bm25 = Bm25Service()
        self._pg_search = PostgresSearchService()
        self._source_consistency = SourceConsistencyService()
        self._quality = ChunkQualityService()
        self._flags = FeatureFlagService()
        self._answer_policy = AnswerPolicyService()

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]]]:
        routed = self._route_request(request)
        results, retrieval_route = await self._retrieve(routed, session=session)
        chunk_ids = [r.get("chunk_id", "") for r in results]
        answer_text, citations = await self._llm.generate_answer(
            request.question, results, history, request.query_mode, request.audience,
        )
        citations = self._source_consistency.filter_citations(citations, results)
        answer_text, citations, disclaimer = self._answer_policy.finalize_answer(
            answer_text, citations, results, request.audience,
        )
        self._enrich_citations(citations, results)
        quality = answer_quality_service.package(request, results, retrieval_route, len(citations))
        response = AnswerResponse(
            answer=answer_text,
            conversation_id=request.conversation_id or "",
            citations=citations,
            disclaimer=disclaimer,
            retrieval_route=retrieval_route,
            confidence_score=quality["confidence_score"],  # type: ignore[arg-type]
            verification_questions=quality["verification_questions"],  # type: ignore[arg-type]
        )
        return response, chunk_ids, results

    async def query_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        is_layperson = request.audience == "layperson"
        yield {"step": "search", "message": "Ik bekijk de relevante EU-regels..." if is_layperson else "Zoeken in EU-documenten..."}
        routed = self._route_request(request)
        yield {
            "step": "router",
            "message": "Ik bepaal de juiste juridische zoekroute..." if is_layperson else "Router bepaalt retrievalstrategie...",
            "detail": {"route": routed.filters.model_dump() if routed.filters else {}},
        }
        results, retrieval_route = await self._retrieve(routed, session=session)
        yield {
            "step": "found",
            "message": "Relevante regels gevonden" if is_layperson else f"{len(results)} relevante artikelen gevonden",
            "detail": {
                "count": len(results),
                "audience": request.audience,
                "retrieval_route": retrieval_route,
                "chunk_ids": [r.get("chunk_id", "") for r in results],
                "retrieval_chunks": results,
            },
        }
        consolidated = self._trust.prefer_consolidated(results)
        yield {"step": "versions", "message": "Ik selecteer de meest actuele officiële versies..." if is_layperson else "Meest recente geconsolideerde versies geselecteerd"}
        yield {"step": "generating", "message": "Ik stel een antwoord voor u samen..." if is_layperson else "Antwoord wordt samengesteld..."}
        answer_text, citations = await self._llm.generate_answer(
            request.question, consolidated, history, request.query_mode, request.audience,
        )
        citations = self._source_consistency.filter_citations(citations, consolidated)
        answer_text, citations, disclaimer = self._answer_policy.finalize_answer(
            answer_text, citations, consolidated, request.audience,
        )
        self._enrich_citations(citations, consolidated)
        quality = answer_quality_service.package(request, consolidated, retrieval_route, len(citations))
        yield {
            "step": "complete",
            "message": "Klaar",
            "detail": {
                "answer": answer_text,
                "conversation_id": request.conversation_id,
                "citations": [c.model_dump(mode="json") for c in citations],
                "disclaimer": disclaimer,
                "retrieval_route": retrieval_route,
                "confidence_score": quality["confidence_score"],
                "verification_questions": quality["verification_questions"],
            },
        }

    async def _retrieve(
        self,
        request: QueryRequest,
        session: AsyncSession | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        filters = request.filters
        lang = filters.language if filters else request.language
        in_force = filters.in_force_only if filters else True
        if filters and filters.time_context == "historical":
            in_force = False
        cache_key = self._cache.build_key(request.question, lang or "nl", in_force)
        cached = await self._cache.get(cache_key)
        if cached:
            metrics_service.record_cache_hit()
            metrics_service.record_route("cache")
            return cached, "cache"
        if session is not None:
            persisted = await self._cache.get_persisted_chunks(session, cache_key)
            if persisted:
                await self._cache.set(cache_key, persisted)
                metrics_service.record_cache_hit()
                metrics_service.record_route("cache")
                return persisted, "cache"
        vector = self._embeddings.embed_query(request.question)
        budget = RetrievalBudget(settings.retrieval_budget_seconds)
        budget.ensure("vector_search")
        dense = self._qdrant.search(vector, limit=RETRIEVAL_CANDIDATE_LIMIT, language=lang, in_force_only=in_force, filters=filters)
        bm25_ranked = self._bm25.rank(request.question, dense, top_k=50)
        pg_ranked: list[dict[str, Any]] = []
        if session is not None:
            pg_ranked = await self._pg_search.search(session, request.question, lang, limit=50)
        hint_query = filters.celex if filters and filters.celex else request.question
        hint_hits = self._hint_search(hint_query, lang, in_force)
        if self._flags.is_hybrid_rrf_enabled():
            merged = reciprocal_rank_fusion(hint_hits, dense, bm25_ranked, pg_ranked, k=settings.rrf_k)
        else:
            merged = self._merge_results(hint_hits, dense, bm25_ranked)
        merged = self._apply_post_filters(merged, filters)
        if filters and filters.consolidated_preferred:
            merged = self._trust.prefer_consolidated(merged)
        reranked = self._reranker.rerank(request.question, merged)
        reranked = self._quality.filter_chunks(reranked)
        reranked = deduplicate_chunks(reranked, max_chunks=settings.rerank_top_k)
        if self._should_live_fallback(reranked):
            try:
                budget.ensure("live_fallback")
            except RetrievalBudgetExceeded:
                logger.warning("Skipping live fallback due to retrieval budget")
                route = "hybrid" if hint_hits or bm25_ranked else "local"
                await self._cache.set(cache_key, reranked)
                metrics_service.record_route(route)
                return reranked, route
            celex_hint = filters.celex if filters else None
            live_chunks = await self._live.fallback_chunks(
                request.question,
                lang or "nl",
                celex_hint=celex_hint,
            )
            metrics_service.record_fallback(bool(live_chunks))
            if live_chunks:
                await self._cache.set(cache_key, live_chunks)
                metrics_service.record_route("live_fallback")
                return live_chunks, "live_fallback"
        route = "hybrid" if hint_hits or bm25_ranked else "local"
        if hint_hits:
            output = self._merge_results(hint_hits, reranked)[:8]
            await self._cache.set(cache_key, output)
            metrics_service.record_route("hybrid")
            return output, "hybrid"
        await self._cache.set(cache_key, reranked)
        metrics_service.record_route(route)
        return reranked, route

    def _enrich_citations(self, citations: list, chunks: list[dict]) -> None:
        chunk_map = {chunk.get("celex"): chunk for chunk in chunks}
        for cite in citations:
            chunk = chunk_map.get(cite.celex) or (chunks[0] if chunks else {})
            self._trust.enrich_citation(cite, chunk)
            cite.legal_citation = self._citations.to_legal_format(cite)

    def _should_live_fallback(self, chunks: list[dict[str, Any]]) -> bool:
        if not self._flags.is_live_fallback_enabled():
            return False
        if not chunks:
            return True
        scores = [float(chunk.get("score", 0.0)) for chunk in chunks]
        return max(scores, default=0.0) < settings.fallback_score_threshold

    def _route_request(self, request: QueryRequest) -> QueryRequest:
        route = self._router.route(request.question, request.language)
        existing = request.filters.model_dump() if request.filters else {}
        merged_filters: dict[str, object] = {
            "domain": existing.get("domain") or (route.domains[0] if route.domains else None),
            "doc_type": existing.get("doc_type") or (route.doc_types[0] if route.doc_types else None),
            "celex": existing.get("celex") or route.celex_hint,
            "language": existing.get("language") or route.language,
            "time_context": existing.get("time_context") or route.time_context,
            "in_force_only": existing.get("in_force_only", route.time_context != "historical"),
            "consolidated_preferred": existing.get("consolidated_preferred", True),
        }
        return request.model_copy(update={"filters": QueryFilters(**merged_filters)})

    def _apply_post_filters(self, chunks: list[dict[str, Any]], filters: QueryFilters | None) -> list[dict[str, Any]]:
        if not filters:
            return chunks
        output = chunks
        if filters.doc_type:
            output = [c for c in output if doc_type_matches_celex(filters.doc_type, c.get("celex", ""))]
        if filters.domain:
            terms = DOMAIN_KEYWORDS.get(filters.domain, ())
            output = [c for c in output if self._matches_domain(c, terms)]
        return output

    def _matches_domain(self, chunk: dict[str, Any], terms: tuple[str, ...]) -> bool:
        if not terms:
            return True
        text = f"{chunk.get('title', '')} {chunk.get('text', '')}".lower()
        return any(term in text for term in terms)

    def _hint_search(self, query: str, language: str | None, in_force_only: bool) -> list[dict]:
        target_celex = match_celex_hints(query)
        if not target_celex:
            return []
        return self._qdrant.search_by_celex(celex_values=target_celex, limit=12, language=language, in_force_only=in_force_only)

    def _merge_results(self, *result_groups: list[dict]) -> list[dict]:
        seen: set[str] = set()
        merged: list[dict] = []
        for group in result_groups:
            for result in group:
                cid = result.get("chunk_id")
                if cid and cid not in seen:
                    seen.add(cid)
                    merged.append(result)
        return merged
