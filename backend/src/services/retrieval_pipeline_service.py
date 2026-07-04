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
from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.services.live_retrieval_service import LiveRetrievalService
from backend.src.services.metrics_service import metrics_service
from backend.src.services.postgres_search_service import PostgresSearchService
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.query_cache_service import QueryCacheService
from backend.src.services.reranker_service import RerankerService
from backend.src.services.retrieval_explainability_service import (
    DiscoveryContext,
    RetrievalExplainabilityService,
    StageCounts,
)
from backend.src.services.trust_indicator_service import TrustIndicatorService
from backend.src.utils.article_chunk_filter import (
    chunks_include_planned_articles,
    filter_chunks_by_articles_strict,
)
from backend.src.utils.celex_hint_resolver import (
    cached_chunks_are_usable,
    has_usable_celex_chunks,
    resolve_live_celex_hint,
    resolve_source_plan,
    should_force_hint_live_fallback,
)
from backend.src.utils.context_dedup import deduplicate_chunks
from backend.src.utils.planned_article_cache import cached_includes_planned_articles
from backend.src.utils.qdrant_resilience import safe_dense_search
from backend.src.utils.retrieval_budget import RetrievalBudget
from backend.src.utils.retrieval_discovery_bootstrap import build_discovery_context, hint_search
from backend.src.utils.retrieval_pipeline_fallback import run_pipeline_live_fallback
from backend.src.utils.retrieval_merge import merge_deduped_results
from backend.src.utils.retrieval_post_filters import apply_retrieval_post_filters
from backend.src.utils.rrf_fusion import reciprocal_rank_fusion
from shared.schemas.query import QueryFilters, QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability

logger = logging.getLogger(__name__)

RETRIEVAL_CANDIDATE_LIMIT = 200

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
        self._discovery = CelexDiscoveryService()

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
        discovery_candidates = await self._discovery.discover(request.question, lang or "nl")
        discovery_ctx = build_discovery_context(discovery_candidates)
        celex_hint = resolve_live_celex_hint(
            request.question, filters, None, discovery_candidates,
        )
        source_plan = resolve_source_plan(request.question, discovery_candidates)
        cache_key = self._cache.build_key(request.question, lang or "nl", in_force, filters)
        cached = await self._cache.get(cache_key)
        if cached and celex_hint and not cached_chunks_are_usable(cached, celex_hint):
            cached = None
        if cached and source_plan and source_plan.articles:
            if not cached_includes_planned_articles(cached, source_plan.articles):
                cached = None
        if cached:
            metrics_service.record_cache_hit()
            cached = self._deprecation.filter_chunks(cached, filters)
            cached = self._versions.resolve_retrieval_chunks(cached, filters)
            return self._finish(request, cached, "cache", StageCounts(final=len(cached)), discovery_ctx)
        if session is not None:
            persisted = await self._cache.get_persisted_chunks(session, cache_key)
            if persisted and celex_hint and not cached_chunks_are_usable(persisted, celex_hint):
                persisted = []
            if persisted:
                persisted = self._deprecation.filter_chunks(persisted, filters)
                persisted = self._versions.resolve_retrieval_chunks(persisted, filters)
                await self._cache.set(cache_key, persisted, request.question)
                metrics_service.record_cache_hit()
                return self._finish(
                    request, persisted, "cache", StageCounts(final=len(persisted)), discovery_ctx,
                )
        counts = StageCounts()
        vector = self._embeddings.embed_query(request.question)
        budget = RetrievalBudget(settings.retrieval_budget_seconds)
        budget.ensure("vector_search")
        excluded_celex = self._deprecation.excluded_celex_for_filters(filters, lang)
        dense = safe_dense_search(
            self._qdrant, vector, RETRIEVAL_CANDIDATE_LIMIT, lang, in_force, filters, excluded_celex,
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
        hint_hits = hint_search(
            self._qdrant, self._deprecation, request.question, lang, in_force, filters,
        )
        counts.hints = len(hint_hits)
        hybrid = self._flags.is_hybrid_rrf_enabled()
        merged = (
            reciprocal_rank_fusion(hint_hits, dense, bm25_ranked, pg_ranked, k=settings.rrf_k)
            if hybrid
            else merge_deduped_results(hint_hits, dense, bm25_ranked)
        )
        counts.merged = len(merged)
        merged = apply_retrieval_post_filters(merged, filters)
        merged = self._deprecation.filter_chunks(merged, filters)
        merged = self._versions.resolve_retrieval_chunks(merged, filters)
        if filters and filters.consolidated_preferred:
            merged = self._trust.prefer_consolidated(merged)
        if not merged and celex_hint:
            finished = await run_pipeline_live_fallback(
                request, budget, cache_key, lang, filters, hint_hits, bm25_ranked, [],
                counts, celex_hint, discovery_ctx,
                self._live, self._cache, self._deprecation, self._flags, self._finish,
            )
            if finished is not None:
                return finished
        reranked = self._reranker.rerank(request.question, merged)
        reranked = self._quality.filter_chunks(reranked)
        reranked = deduplicate_chunks(reranked, max_chunks=settings.rerank_top_k)
        if source_plan and source_plan.articles:
            planned = filter_chunks_by_articles_strict(reranked, source_plan.articles)
            reranked = planned if planned else []
        counts.final = len(reranked)
        if celex_hint and has_usable_celex_chunks(hint_hits, celex_hint):
            hint_output = hint_hits
            if source_plan and source_plan.articles:
                planned_hints = filter_chunks_by_articles_strict(hint_hits, source_plan.articles)
                if planned_hints:
                    hint_output = planned_hints
                elif not reranked:
                    hint_output = []
            if hint_output and (not source_plan or not source_plan.articles or chunks_include_planned_articles(hint_output, source_plan.articles)):
                output = merge_deduped_results(hint_output, reranked)[:8]
                counts.final = len(output)
                await self._cache.set(cache_key, output, request.question)
                return self._finish(request, output, "hybrid", counts, discovery_ctx)
        if (
            should_force_hint_live_fallback(hint_hits, reranked, celex_hint)
            or self._should_live_fallback(reranked)
            or (source_plan and not has_usable_celex_chunks(reranked, source_plan.celex))
            or (
                source_plan
                and source_plan.articles
                and not chunks_include_planned_articles(reranked, source_plan.articles)
            )
        ):
            finished = await run_pipeline_live_fallback(
                request, budget, cache_key, lang, filters, hint_hits, bm25_ranked, reranked,
                counts, celex_hint, discovery_ctx,
                self._live, self._cache, self._deprecation, self._flags, self._finish,
            )
            if finished is not None:
                return finished
        route = "hybrid" if hint_hits or bm25_ranked else "local"
        if hint_hits:
            output = merge_deduped_results(hint_hits, reranked)[:8]
            counts.final = len(output)
            await self._cache.set(cache_key, output, request.question)
            return self._finish(request, output, "hybrid", counts, discovery_ctx)
        await self._cache.set(cache_key, reranked, request.question)
        return self._finish(request, reranked, route, counts, discovery_ctx)

    def _finish(
        self,
        request: QueryRequest,
        chunks: list[dict[str, Any]],
        route: str,
        counts: StageCounts,
        discovery: DiscoveryContext | None = None,
    ) -> tuple[list[dict[str, Any]], str, RetrievalExplainability]:
        metrics_service.record_route(route)
        explainability = self._explain.build(
            route, request, counts, self._reranker, self._flags.is_hybrid_rrf_enabled(), chunks,
            discovery,
        )
        return chunks, route, explainability

    def _should_live_fallback(self, chunks: list[dict[str, Any]]) -> bool:
        if not chunks:
            return True
        scores = [float(chunk.get("score", 0.0)) for chunk in chunks]
        return max(scores, default=0.0) < settings.fallback_score_threshold
