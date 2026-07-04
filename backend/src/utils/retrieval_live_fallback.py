"""Live EUR-Lex fallback helpers for the retrieval pipeline."""
import logging
from typing import Any

from backend.src.config import settings
from backend.src.services.document_deprecation_service import DocumentDeprecationService
from backend.src.services.feature_flag_service import FeatureFlagService
from backend.src.services.live_retrieval_service import LiveRetrievalService
from backend.src.services.metrics_service import metrics_service
from backend.src.services.query_cache_service import QueryCacheService
from backend.src.utils.celex_hint_resolver import has_usable_celex_chunks, resolve_live_celex_hint
from backend.src.utils.retrieval_budget import RetrievalBudget, RetrievalBudgetExceeded
from shared.schemas.query import QueryFilters, QueryRequest

logger = logging.getLogger(__name__)


def should_force_live_despite_budget(
    celex_hint: str | None,
    hint_hits: list[dict[str, Any]],
    reranked: list[dict[str, Any]],
) -> bool:
    """Force live fetch when local index missed a known CELEX target."""
    if not celex_hint:
        return False
    if reranked:
        return False
    return not has_usable_celex_chunks(hint_hits, celex_hint)


async def try_live_fallback(
    request: QueryRequest,
    budget: RetrievalBudget,
    cache_key: str,
    lang: str | None,
    filters: QueryFilters | None,
    hint_hits: list[dict[str, Any]],
    bm25_ranked: list[dict[str, Any]],
    reranked: list[dict[str, Any]],
    live: LiveRetrievalService,
    cache: QueryCacheService,
    deprecation: DocumentDeprecationService,
    flags: FeatureFlagService,
    celex_hint_override: str | None = None,
) -> tuple[list[dict[str, Any]], str] | None:
    """Fetch live chunks when local retrieval is empty or unusable."""
    if not flags.is_live_fallback_enabled():
        return None
    force = should_force_live_despite_budget(celex_hint_override, hint_hits, reranked)
    try:
        budget.ensure("live_fallback")
    except RetrievalBudgetExceeded:
        if not force:
            logger.warning("Skipping live fallback due to retrieval budget")
            route = "hybrid" if hint_hits or bm25_ranked else "local"
            await cache.set(cache_key, reranked, request.question)
            return reranked, route
        logger.warning(
            "Retrieval budget exceeded; forcing live fallback for CELEX %s",
            celex_hint_override,
        )
    celex_hint = resolve_live_celex_hint(request.question, filters, celex_hint_override)
    if celex_hint:
        logger.info("Live fallback using CELEX hint %s", celex_hint)
    allowed = lambda celex, allowed_lang: deprecation.is_celex_allowed(celex, allowed_lang, filters)
    live_chunks = await live.fallback_chunks(
        request.question,
        lang or "nl",
        celex_hint=celex_hint,
        is_celex_allowed=allowed,
    )
    live_chunks = deprecation.filter_chunks(live_chunks, filters)
    metrics_service.record_fallback(bool(live_chunks))
    if not live_chunks:
        return None
    await cache.set(cache_key, live_chunks, request.question)
    return live_chunks, "live_fallback"
