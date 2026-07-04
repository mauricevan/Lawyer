"""Retry retrieval within legal domain when evidence validation fails."""
import logging
from typing import Any

from backend.src.services.article_fetch_orchestrator_service import ArticleFetchOrchestratorService
from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.services.conflict_aware_celex_resolver_service import ConflictAwareCelexResolverService
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.legal_domain_retrieval_filter import (
    default_instrument_for_domain,
    is_celex_allowed_for_domain,
)
from backend.src.utils.hypothesis_retrieval_query import build_hypothesis_retrieval_query
from shared.schemas.celex_resolution import CelexResolutionResult
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

logger = logging.getLogger(__name__)
_MAX_RETRY_INSTRUMENTS = 2


class EvidenceRetrievalRetryService:
    """Fetch additional domain-consistent instruments after evidence FAIL."""

    def __init__(self) -> None:
        self._fetcher = ArticleFetchOrchestratorService()
        self._discovery = CelexDiscoveryService()
        self._planner = LegalSourcePlannerService()
        self._celex_resolver = ConflictAwareCelexResolverService()

    async def retry(
        self,
        request: QueryRequest,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        session: Any | None = None,
        hypothesis: LegalHypothesis | None = None,
        analysis: LegalCaseAnalysis | None = None,
        celex_resolution: CelexResolutionResult | None = None,
    ) -> AgentFetchResult:
        """Merge extra chunks from same-domain instruments not yet attempted."""
        attempted = set(fetch.attempted_celex)
        if analysis:
            extras = self._conflict_retry_instruments(analysis, plan, attempted, celex_resolution)
        else:
            retrieval_query = build_hypothesis_retrieval_query(hypothesis) if hypothesis else request.question
            extras = await self._candidate_instruments(request, plan, attempted, retrieval_query)
        if not extras:
            return fetch
        retry_plan = plan.model_copy(update={"instruments": extras[:_MAX_RETRY_INSTRUMENTS]})
        retry_fetch = await self._fetcher.fetch(retry_plan, request, session)
        merged = _dedupe_chunks(fetch.chunks + retry_fetch.chunks)
        return AgentFetchResult(
            chunks=merged,
            fetch_ok=fetch.fetch_ok or retry_fetch.fetch_ok,
            fetch_source=_merge_source(fetch.fetch_source, retry_fetch.fetch_source),
            attempted_celex=list(attempted | set(retry_fetch.attempted_celex)),
            resolved_celex=list({*fetch.resolved_celex, *retry_fetch.resolved_celex}),
            articles_fetched=_merge_articles(fetch.articles_fetched, retry_fetch.articles_fetched),
            fetch_attempted=True,
        )

    def _conflict_retry_instruments(
        self,
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        attempted: set[str],
        prior_resolution: CelexResolutionResult | None,
    ) -> list[InstrumentTarget]:
        """V5.1: domain-level re-retrieval via conflict resolver — not planner retry."""
        resolution = self._celex_resolver.resolve(analysis, plan)
        return [
            item for item in resolution.instruments
            if item.celex and item.celex not in attempted
        ][: _MAX_RETRY_INSTRUMENTS]

    async def _candidate_instruments(
        self,
        request: QueryRequest,
        plan: LegalInterpretationPlan,
        attempted: set[str],
        retrieval_query: str,
    ) -> list[InstrumentTarget]:
        candidates: list[InstrumentTarget] = []
        seen: set[str] = set(attempted)
        for instrument in self._from_rule_plan(retrieval_query, plan, seen):
            candidates.append(instrument)
            seen.add(instrument.celex or "")
        for instrument in self._from_domain_default(retrieval_query, plan, seen):
            if instrument.celex not in seen:
                candidates.append(instrument)
                seen.add(instrument.celex or "")
        for instrument in await self._from_discovery(retrieval_query, request.language, plan, seen):
            if instrument.celex not in seen:
                candidates.append(instrument)
                seen.add(instrument.celex or "")
            if len(candidates) >= _MAX_RETRY_INSTRUMENTS:
                break
        return candidates[:_MAX_RETRY_INSTRUMENTS]

    def _from_rule_plan(
        self,
        retrieval_query: str,
        plan: LegalInterpretationPlan,
        seen: set[str],
    ) -> list[InstrumentTarget]:
        rule = self._planner.plan(retrieval_query)
        if not rule or rule.celex in seen:
            return []
        if not is_celex_allowed_for_domain(rule.celex, plan.legal_domain):
            return []
        return [InstrumentTarget(
            name=rule.plan_id,
            celex=rule.celex,
            articles=list(rule.articles),
            confidence=0.65,
        )]

    def _from_domain_default(
        self,
        retrieval_query: str,
        plan: LegalInterpretationPlan,
        seen: set[str],
    ) -> list[InstrumentTarget]:
        fallback = default_instrument_for_domain(plan.legal_domain, retrieval_query)
        if not fallback or not fallback.celex or fallback.celex in seen:
            return []
        return [fallback]

    async def _from_discovery(
        self,
        retrieval_query: str,
        language: str,
        plan: LegalInterpretationPlan,
        seen: set[str],
    ) -> list[InstrumentTarget]:
        hits = await self._discovery.discover(retrieval_query, language, limit=5)
        found: list[InstrumentTarget] = []
        for hit in hits:
            if hit.celex in seen:
                continue
            if not is_celex_allowed_for_domain(hit.celex, plan.legal_domain):
                continue
            found.append(InstrumentTarget(
                name=hit.title or hit.celex,
                celex=hit.celex,
                articles=[],
                confidence=hit.score,
                title=hit.title,
            ))
            if len(found) >= _MAX_RETRY_INSTRUMENTS:
                break
        return found


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


def _merge_source(left: str, right: str) -> str:
    if left == right:
        return left
    return "mixed"


def _merge_articles(left: list[str], right: list[str]) -> list[str]:
    return sorted(set(left) | set(right), key=lambda n: int(n) if n.isdigit() else n)
