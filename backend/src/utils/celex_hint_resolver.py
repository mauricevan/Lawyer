"""Resolve CELEX hints for live EUR-Lex fallback."""
import logging
from typing import Any

from backend.src.services.celex_discovery_service import CelexCandidate, CelexDiscoveryService
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.context_quality_service import USABLE_SCORE_THRESHOLD
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from ingestion.src.data.legal_term_hints import match_primary_celex_hint
from shared.schemas.query import QueryFilters

logger = logging.getLogger(__name__)
_quality = ChunkQualityService()
_planner = LegalSourcePlannerService()
_discovery = CelexDiscoveryService()
_HIGH_DISCOVERY_SCORE = 0.75


def resolve_discovery_candidates(question: str, limit: int = 5) -> list[CelexCandidate]:
    """Return ranked CELEX discovery candidates for a question."""
    return _discovery.discover_sync(question, limit=limit)


def merge_discovery_celex_set(question: str, base: set[str] | None = None) -> set[str]:
    """Merge term hints with discovery candidates above minimum score."""
    from ingestion.src.data.legal_term_hints import match_celex_hints

    merged = set(base or match_celex_hints(question))
    for candidate in _discovery.discover_sync(question, limit=3):
        if candidate.score >= 0.5:
            merged.add(candidate.celex)
    return merged


def resolve_live_celex_hint(
    question: str,
    filters: QueryFilters | None,
    oj_celex_override: str | None = None,
    discovery: list[CelexCandidate] | None = None,
) -> str | None:
    """Pick CELEX for live fallback: override, filter, discovery, planner, then hints."""
    if oj_celex_override:
        return oj_celex_override
    if filters and filters.celex:
        return filters.celex
    candidates = discovery if discovery is not None else _discovery.discover_sync(question)
    if candidates and candidates[0].score >= _HIGH_DISCOVERY_SCORE:
        return candidates[0].celex
    plan = _planner.plan(question, discovery_candidates=candidates)
    if plan and plan.plan_id != "discovery":
        if candidates and candidates[0].score >= _HIGH_DISCOVERY_SCORE:
            if plan.celex != candidates[0].celex:
                logger.info(
                    "Discovery CELEX %s overrides planner %s",
                    candidates[0].celex,
                    plan.celex,
                )
                return candidates[0].celex
        return plan.celex
    if plan:
        return plan.celex
    if candidates and candidates[0].score >= 0.5:
        return candidates[0].celex
    return match_primary_celex_hint(question)


def resolve_source_plan(question: str, discovery: list[CelexCandidate] | None = None):
    candidates = discovery if discovery is not None else _discovery.discover_sync(question)
    return _planner.plan(question, discovery_candidates=candidates)


def chunks_include_celex(chunks: list[dict[str, Any]], celex: str) -> bool:
    return any(chunk.get("celex") == celex for chunk in chunks)


def has_usable_celex_chunks(chunks: list[dict[str, Any]], celex: str) -> bool:
    matching = [chunk for chunk in chunks if chunk.get("celex") == celex]
    if not matching:
        return False
    for chunk in matching:
        text = str(chunk.get("text", "")).strip()
        score = float(chunk.get("score", 0.0) or chunk.get("rerank_score", 0.0))
        if score >= USABLE_SCORE_THRESHOLD and len(text) >= 40:
            return True
        if not _quality.is_usable_legal_text(text):
            continue
        if len(text) >= 200:
            return True
        if len(text) >= 100 and _quality.usable_score(text) >= 0.15:
            return True
    return False


def should_force_hint_live_fallback(
    hint_hits: list[dict[str, Any]],
    reranked: list[dict[str, Any]],
    celex_hint: str | None,
) -> bool:
    if not celex_hint:
        return False
    if has_usable_celex_chunks(hint_hits, celex_hint):
        return False
    if has_usable_celex_chunks(reranked, celex_hint):
        return False
    if not hint_hits:
        logger.info("CELEX hint %s matched but local index returned no chunks", celex_hint)
        return True
    if not chunks_include_celex(reranked, celex_hint):
        logger.info("CELEX hint %s missing from reranked chunks; forcing live fallback", celex_hint)
        return True
    logger.info("CELEX hint %s present but unusable locally; forcing live fallback", celex_hint)
    return True


def cached_chunks_are_usable(chunks: list[dict[str, Any]], celex_hint: str | None) -> bool:
    if not chunks:
        return False
    if celex_hint:
        if not chunks_include_celex(chunks, celex_hint):
            return False
        return has_usable_celex_chunks(chunks, celex_hint)
    from backend.src.services.context_quality_service import ContextQualityService

    return ContextQualityService().assess(chunks).is_usable
