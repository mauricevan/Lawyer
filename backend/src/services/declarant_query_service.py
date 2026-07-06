"""HTTP adapter for the declarant layperson pipeline."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.services.declarant_pipeline_service import DeclarantPipelineService
from shared.schemas.query import AnswerResponse, QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability, RouterDecision


class DeclarantQueryService:
    """Layperson queries via think→fetch→verify pipeline."""

    def __init__(self) -> None:
        self._pipeline = DeclarantPipelineService()

    @staticmethod
    def is_enabled() -> bool:
        return settings.declarant_pipeline_enabled

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]], RetrievalExplainability]:
        plan, fetch, bundle, hypothesis = await self._pipeline.run(request, history, session)
        chunk_ids = [c.get("chunk_id", "") for c in fetch.chunks if c.get("chunk_id")]
        explain = RetrievalExplainability(
            route="declarant_flow",
            query_language=request.language or "nl",
            router=RouterDecision(),
            reranker_variant="declarant",
            rerank_latency_ms=0.0,
            hybrid_rrf_enabled=False,
            chunk_count=len(fetch.chunks),
            interpretation_plan=plan.model_dump(mode="json"),
            resolved_celex=[inst.celex for inst in plan.instruments if inst.celex],
            articles_fetched=fetch.articles_fetched,
            fetch_source=fetch.fetch_source,
        )
        response = AnswerResponse(
            answer=bundle["answer_text"],
            conversation_id=request.conversation_id or "",
            citations=bundle["citations"],
            disclaimer=bundle["disclaimer"],
            retrieval_route="declarant_flow",
            confidence_score=bundle["quality"].get("confidence_score"),  # type: ignore[arg-type]
            verification_questions=bundle["quality"].get("verification_questions", []),  # type: ignore[arg-type]
            clarification_prompt=bundle["quality"].get("clarification_prompt"),
            retrieval_explainability=explain,
            coverage_guidance=bundle.get("coverage_guidance"),
            coverage_status=bundle["coverage_status"],
            legal_hypothesis=hypothesis if request.audience == "professional" else None,
        )
        return response, chunk_ids, fetch.chunks, explain

    async def query_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        async for event in self._pipeline.run_with_events(request, history, session):
            yield event
