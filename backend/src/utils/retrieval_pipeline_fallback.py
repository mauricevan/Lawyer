"""Live fallback completion step for retrieval pipeline."""
from typing import Any

from backend.src.services.query_cache_service import QueryCacheService
from backend.src.services.retrieval_explainability_service import DiscoveryContext, StageCounts
from backend.src.utils.article_chunk_filter import filter_chunks_by_articles_strict
from backend.src.utils.celex_hint_resolver import resolve_source_plan
from backend.src.utils.retrieval_budget import RetrievalBudget
from backend.src.utils.retrieval_live_fallback import try_live_fallback
from shared.schemas.query import QueryFilters, QueryRequest


async def run_pipeline_live_fallback(
    request: QueryRequest,
    budget: RetrievalBudget,
    cache_key: str,
    lang: str | None,
    filters: QueryFilters | None,
    hint_hits: list[dict],
    bm25_ranked: list[dict],
    reranked: list[dict],
    counts: StageCounts,
    celex_hint: str | None,
    discovery_ctx: DiscoveryContext,
    live,
    cache: QueryCacheService,
    deprecation,
    flags,
    finish,
) -> tuple[list[dict[str, Any]], str, Any] | None:
    fallback = await try_live_fallback(
        request, budget, cache_key, lang, filters, hint_hits, bm25_ranked, reranked,
        live, cache, deprecation, flags, celex_hint,
    )
    if fallback is None:
        return None
    chunks, route = fallback
    discovery_ctx.live_fallback_forced = True
    counts.final = len(chunks)
    plan = resolve_source_plan(request.question)
    if plan and plan.articles and chunks:
        planned = filter_chunks_by_articles_strict(chunks, plan.articles)
        if planned:
            chunks = planned
            counts.final = len(chunks)
    return finish(request, chunks, route, counts, discovery_ctx)
