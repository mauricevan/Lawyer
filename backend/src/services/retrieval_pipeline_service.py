"""Hybrid retrieval pipeline with explainability metadata (plan12 AB)."""
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.services.bm25_service import Bm25Service
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.document_deprecation_service import DocumentDeprecationService
from backend.src.services.document_version_conflict_service import DocumentVersionConflictService
from backend.src.services.embedding_service import get_embedding_service
from backend.src.services.feature_flag_service import FeatureFlagService
from backend.src.services.live_retrieval_service import LiveRetrievalService
from backend.src.services.metrics_service import metrics_service
from backend.src.services.postgres_search_service import PostgresSearchService
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.query_cache_service import QueryCacheService
from backend.src.services.reranker_service import RerankerService
from backend.src.services.retrieval_explainability_service import (
    RetrievalExplainabilityService,
    StageCounts,
)
from backend.src.services.trust_indicator_service import TrustIndicatorService
from backend.src.utils.context_dedup import deduplicate_chunks
from backend.src.utils.qdrant_filters import doc_type_matches_celex
from backend.src.utils.retrieval_budget import RetrievalBudget, RetrievalBudgetExceeded
from backend.src.utils.rrf_fusion import reciprocal_rank_fusion
from ingestion.src.data.domain_registry_loader import get_domain_keywords
from ingestion.src.data.legal_term_hints import match_celex_hints
from shared.schemas.query import QueryFilters, QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability

logger = logging.getLogger(__name__)

RETRIEVAL_CANDIDATE_LIMIT = 200
DOMAIN_KEYWORDS = get_domain_keywords()


class RetrievalPipelineService:
    """Executes hybrid search, reranking, and optional live fallback."""

    def __init__(self, reranker: RerankerService | None = None) -> None:
        self._embeddings = get_embedding_service()
        self._qdrant = QdrantService()
        self._reranker = reranker or RerankerService()
        self._trust = TrustIndicatorService()
        self._live = LiveRetrievalService()
        self._cache = QueryCacheService()
        self._bm25 = Bm25Service()
        self._pg_search = PostgresSearchService()
        self._quality = ChunkQualityService()
        self._flags = FeatureFlagService()
        self._explain = RetrievalExplainabilityService()
        self._deprecation = DocumentDeprecationService()
        self._versions = DocumentVersionConflictService()

    async def retrieve(
        self,
        request: QueryRequest,
        session: AsyncSession | None = None,
    ) -> tuple[list[dict[str, Any]], str, RetrievalExplainability]:
        filters = request.filters
        lang = filters.language if filters else request.language
        in_force = filters.in_force_only if filters else True
        if filters and filters.time_context == "historical":
            in_force = False
        cache_key = self._cache.build_key(request.question, lang or "nl", in_force)
        cached = await self._cache.get(cache_key)
        if cached:
            metrics_service.record_cache_hit()
            cached = self._deprecation.filter_chunks(cached, filters)
            cached = self._versions.resolve_retrieval_chunks(cached, filters)
            return self._finish(request, cached, "cache", StageCounts(final=len(cached)))
        if session is not None:
            persisted = await self._cache.get_persisted_chunks(session, cache_key)
            if persisted:
                persisted = self._deprecation.filter_chunks(persisted, filters)
                persisted = self._versions.resolve_retrieval_chunks(persisted, filters)
                await self._cache.set(cache_key, persisted)
                metrics_service.record_cache_hit()
                return self._finish(request, persisted, "cache", StageCounts(final=len(persisted)))
        counts = StageCounts()
        vector = self._embeddings.embed_query(request.question)
        budget = RetrievalBudget(settings.retrieval_budget_seconds)
        budget.ensure("vector_search")
        excluded_celex = self._deprecation.excluded_celex_for_filters(filters, lang)
        dense = self._qdrant.search_with_language_fallback(
            vector,
            limit=RETRIEVAL_CANDIDATE_LIMIT,
            language=lang,
            in_force_only=in_force,
            filters=filters,
            excluded_celex=excluded_celex,
        )
        counts.dense = len(dense)
        bm25_ranked = self._bm25.rank(request.question, dense, top_k=50)
        counts.bm25 = len(bm25_ranked)
        pg_ranked: list[dict[str, Any]] = []
        if session is not None:
            pg_ranked = await self._pg_search.search(
                session, request.question, lang, limit=50, excluded_celex=excluded_celex,
            )
        counts.pg = len(pg_ranked)
        hint_query = filters.celex if filters and filters.celex else request.question
        hint_hits = self._hint_search(hint_query, lang, in_force, filters)
        counts.hints = len(hint_hits)
        hybrid = self._flags.is_hybrid_rrf_enabled()
        if hybrid:
            merged = reciprocal_rank_fusion(hint_hits, dense, bm25_ranked, pg_ranked, k=settings.rrf_k)
        else:
            merged = self._merge_results(hint_hits, dense, bm25_ranked)
        counts.merged = len(merged)
        merged = self._apply_post_filters(merged, filters)
        merged = self._deprecation.filter_chunks(merged, filters)
        merged = self._versions.resolve_retrieval_chunks(merged, filters)
        if filters and filters.consolidated_preferred:
            merged = self._trust.prefer_consolidated(merged)
        reranked = self._reranker.rerank(request.question, merged)
        reranked = self._quality.filter_chunks(reranked)
        reranked = deduplicate_chunks(reranked, max_chunks=settings.rerank_top_k)
        counts.final = len(reranked)
        if self._should_live_fallback(reranked):
            fallback = await self._try_live_fallback(
                request, budget, cache_key, lang, filters, hint_hits, bm25_ranked, reranked,
            )
            if fallback is not None:
                chunks, route = fallback
                counts.final = len(chunks)
                return self._finish(request, chunks, route, counts)
        route = "hybrid" if hint_hits or bm25_ranked else "local"
        if hint_hits:
            output = self._merge_results(hint_hits, reranked)[:8]
            counts.final = len(output)
            await self._cache.set(cache_key, output)
            return self._finish(request, output, "hybrid", counts)
        await self._cache.set(cache_key, reranked)
        return self._finish(request, reranked, route, counts)

    def _finish(
        self,
        request: QueryRequest,
        chunks: list[dict[str, Any]],
        route: str,
        counts: StageCounts,
    ) -> tuple[list[dict[str, Any]], str, RetrievalExplainability]:
        metrics_service.record_route(route)
        explainability = self._explain.build(
            route, request, counts, self._reranker, self._flags.is_hybrid_rrf_enabled(), chunks,
        )
        return chunks, route, explainability

    async def _try_live_fallback(
        self,
        request: QueryRequest,
        budget: RetrievalBudget,
        cache_key: str,
        lang: str | None,
        filters: QueryFilters | None,
        hint_hits: list[dict],
        bm25_ranked: list[dict],
        reranked: list[dict],
    ) -> tuple[list[dict[str, Any]], str] | None:
        if not self._flags.is_live_fallback_enabled():
            return None
        try:
            budget.ensure("live_fallback")
        except RetrievalBudgetExceeded:
            logger.warning("Skipping live fallback due to retrieval budget")
            route = "hybrid" if hint_hits or bm25_ranked else "local"
            await self._cache.set(cache_key, reranked)
            return reranked, route
        celex_hint = filters.celex if filters else None
        live_chunks = await self._live.fallback_chunks(request.question, lang or "nl", celex_hint=celex_hint)
        metrics_service.record_fallback(bool(live_chunks))
        if not live_chunks:
            return None
        await self._cache.set(cache_key, live_chunks)
        return live_chunks, "live_fallback"

    def _should_live_fallback(self, chunks: list[dict[str, Any]]) -> bool:
        if not chunks:
            return True
        scores = [float(chunk.get("score", 0.0)) for chunk in chunks]
        return max(scores, default=0.0) < settings.fallback_score_threshold

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

    def _hint_search(
        self,
        query: str,
        language: str | None,
        in_force_only: bool,
        filters: QueryFilters | None,
    ) -> list[dict]:
        target_celex = match_celex_hints(query)
        if not target_celex:
            return []
        if filters and filters.celex:
            target_celex = {filters.celex}
        else:
            target_celex = self._deprecation.filter_celex_hints(target_celex, filters)
        if not target_celex:
            return []
        return self._qdrant.search_by_celex_with_language_fallback(
            celex_values=target_celex, limit=12, language=language, in_force_only=in_force_only,
        )

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
