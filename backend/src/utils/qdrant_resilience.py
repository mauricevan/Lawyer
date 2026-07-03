"""Safe Qdrant search wrappers for failover resilience (plan14 AB)."""
import logging
from typing import Any

from shared.schemas.query import QueryFilters

logger = logging.getLogger(__name__)


def safe_dense_search(
    qdrant,
    vector: list[float],
    limit: int,
    language: str | None,
    in_force_only: bool,
    filters: QueryFilters | None,
    excluded_celex: set[str],
) -> list[dict[str, Any]]:
    """Run dense search; return empty list when Qdrant is unavailable."""
    try:
        return qdrant.search_with_language_fallback(
            vector,
            limit=limit,
            language=language,
            in_force_only=in_force_only,
            filters=filters,
            excluded_celex=excluded_celex,
        )
    except Exception as exc:
        logger.warning("Qdrant dense search failed: %s", exc.__class__.__name__)
        return []


def safe_celex_hint_search(
    qdrant,
    target_celex: set[str],
    language: str | None,
    in_force_only: bool,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Run CELEX hint search; return empty list when Qdrant is unavailable."""
    try:
        return qdrant.search_by_celex_with_language_fallback(
            celex_values=target_celex,
            limit=limit,
            language=language,
            in_force_only=in_force_only,
        )
    except Exception as exc:
        logger.warning("Qdrant hint search failed: %s", exc.__class__.__name__)
        return []
