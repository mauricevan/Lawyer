"""Declarant FETCH — targeted EUR-Lex retrieval from hypothesis."""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.eurlex_research_service import EurlexResearchService
from backend.src.utils.retrieval_substance import has_substantive_retrieval
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


class DeclarantFetchService:
    """Fetch article text for planned CELEX targets only."""

    def __init__(self) -> None:
        self._research = EurlexResearchService()

    async def fetch(
        self,
        plan: LegalInterpretationPlan,
        request: QueryRequest,
        session: AsyncSession | None = None,
    ) -> AgentFetchResult:
        del session
        result = await self._research.fetch(plan, request)
        result = result.model_copy(update={"fetch_attempted": True})
        if not result.fetch_ok:
            return result
        if not has_substantive_retrieval(result.chunks):
            return result.model_copy(update={"fetch_ok": False})
        return result

    def needs_more_context(self, fetch: AgentFetchResult, plan: LegalInterpretationPlan) -> bool:
        """True when fetch ran but returned nothing usable."""
        return fetch.fetch_attempted and not has_substantive_retrieval(fetch.chunks)
