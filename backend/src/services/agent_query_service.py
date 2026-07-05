"""EUR-Lex Reading Agent — v4 conflict-first pipeline."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.agent_v4_pipeline_service import AgentV4PipelineService
from backend.src.utils.explanation_explainability_builder import build_retrieval_explainability
from shared.schemas.query import AnswerResponse, QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability


class AgentQueryService:
    """v4 agent path: conflict → domain → retrieval → evidence → reconciliation → answer."""

    def __init__(self) -> None:
        self._pipeline = AgentV4PipelineService()

    @staticmethod
    def is_enabled() -> bool:
        from backend.src.config import settings
        return settings.agent_flow_enabled

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]], RetrievalExplainability]:
        resolved, fetch, bundle, hypothesis, evidence, reconciliation, analysis = (
            await self._pipeline.run(request, history, session)
        )
        chunk_ids = [c.get("chunk_id", "") for c in fetch.chunks]
        explain = build_retrieval_explainability(
            resolved, fetch, hypothesis, evidence, reconciliation, analysis,
        )
        response = AnswerResponse(
            answer=bundle["answer_text"],
            conversation_id=request.conversation_id or "",
            citations=bundle["citations"],
            disclaimer=bundle["disclaimer"],
            retrieval_route="agent_flow",
            confidence_score=bundle["quality"]["confidence_score"],  # type: ignore[arg-type]
            verification_questions=bundle["quality"]["verification_questions"],  # type: ignore[arg-type]
            clarification_prompt=bundle["quality"].get("clarification_prompt"),
            retrieval_explainability=explain,
            coverage_guidance=bundle["coverage_guidance"],
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
