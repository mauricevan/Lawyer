"""EUR-Lex Reading Agent query orchestration (ADR-0009 fase 2)."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.services.agent_answer_service import AgentAnswerService
from backend.src.services.article_fetch_orchestrator_service import ArticleFetchOrchestratorService
from backend.src.services.instrument_resolver_service import InstrumentResolverService
from backend.src.services.llm_legal_planner_service import LlmLegalPlannerService
from shared.schemas.legal_interpretation import LegalInterpretationPlan
from shared.schemas.query import AnswerResponse, QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability, RouterDecision


class AgentQueryService:
    """Live-first agent path: interpret → resolve → fetch → answer."""

    def __init__(self) -> None:
        self._planner = LlmLegalPlannerService()
        self._resolver = InstrumentResolverService()
        self._fetcher = ArticleFetchOrchestratorService()
        self._answer = AgentAnswerService()

    @staticmethod
    def is_enabled() -> bool:
        return settings.agent_flow_enabled

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]], RetrievalExplainability]:
        plan, fetch, bundle, explain = await self._run_agent(request, history, session)
        chunk_ids = [c.get("chunk_id", "") for c in fetch.chunks]
        response = AnswerResponse(
            answer=bundle["answer_text"],
            conversation_id=request.conversation_id or "",
            citations=bundle["citations"],
            disclaimer=bundle["disclaimer"],
            retrieval_route="agent_flow",
            confidence_score=bundle["quality"]["confidence_score"],  # type: ignore[arg-type]
            verification_questions=bundle["quality"]["verification_questions"],  # type: ignore[arg-type]
            retrieval_explainability=explain,
            coverage_guidance=bundle["coverage_guidance"],
            coverage_status=bundle["coverage_status"],
        )
        return response, chunk_ids, fetch.chunks, explain

    async def query_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        is_layperson = request.audience == "layperson"
        yield _step(
            "planning",
            "Ik interpreteer uw juridische vraag…" if is_layperson else "Juridische interpretatie…",
        )
        plan = await self._planner.interpret(request.question, history)
        yield _step(
            "resolving",
            "Ik zoek de relevante EU-regelgeving…" if is_layperson else "Instrument resolver…",
            {"interpretation_plan": plan.model_dump(mode="json")},
        )
        resolved = await self._resolver.resolve(plan, request.question, request.language)
        yield _step(
            "fetching",
            "Ik haal artikelteksten op van EUR-Lex…" if is_layperson else "Live artikel-fetch…",
            {"resolved_celex": [i.celex for i in resolved.instruments if i.celex]},
        )
        fetch = await self._fetcher.fetch(resolved, request, session)
        yield _step(
            "verifying",
            "Ik controleer de bronnen…" if is_layperson else "Citation verifier…",
            {
                "articles_fetched": fetch.articles_fetched,
                "fetch_source": fetch.fetch_source,
                "chunk_count": len(fetch.chunks),
            },
        )
        bundle = await self._answer.build(request, fetch, resolved, history)
        explain = _build_explainability(resolved, fetch)
        yield {
            "step": "complete",
            "message": "Klaar",
            "detail": {
                "answer": bundle["answer_text"],
                "conversation_id": request.conversation_id,
                "citations": [c.model_dump(mode="json") for c in bundle["citations"]],
                "disclaimer": bundle["disclaimer"],
                "retrieval_route": "agent_flow",
                "confidence_score": bundle["quality"]["confidence_score"],
                "verification_questions": bundle["quality"]["verification_questions"],
                "retrieval_explainability": explain.model_dump(mode="json"),
                "coverage_guidance": (
                    bundle["coverage_guidance"].model_dump(mode="json")
                    if bundle["coverage_guidance"]
                    else None
                ),
                "coverage_status": bundle["coverage_status"],
                "interpretation_plan": resolved.model_dump(mode="json"),
            },
        }

    async def _run_agent(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> tuple[LegalInterpretationPlan, Any, dict[str, Any], RetrievalExplainability]:
        plan = await self._planner.interpret(request.question, history)
        resolved = await self._resolver.resolve(plan, request.question, request.language)
        fetch = await self._fetcher.fetch(resolved, request, session)
        bundle = await self._answer.build(request, fetch, resolved, history)
        explain = _build_explainability(resolved, fetch)
        return resolved, fetch, bundle, explain


def _step(step: str, message: str, detail: dict | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"step": step, "message": message}
    if detail:
        payload["detail"] = detail
    return payload


def _build_explainability(plan: LegalInterpretationPlan, fetch: Any) -> RetrievalExplainability:
    return RetrievalExplainability(
        route="live_fallback",
        query_language="nl",
        router=RouterDecision(),
        reranker_variant="agent",
        rerank_latency_ms=0.0,
        hybrid_rrf_enabled=False,
        chunk_count=len(fetch.chunks),
        interpretation_plan=plan.model_dump(mode="json"),
        resolved_celex=[i.celex for i in plan.instruments if i.celex],
        articles_fetched=fetch.articles_fetched,
        fetch_source=fetch.fetch_source,
    )
