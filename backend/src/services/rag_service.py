"""Hybrid RAG retrieval and answer orchestration."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.agent_query_service import AgentQueryService
from backend.src.services.answer_bundle_service import AnswerBundleService
from backend.src.services.citation_formatter import CitationFormatter
from backend.src.services.llm_service import LlmService
from backend.src.services.query_router_service import QueryRouterService
from backend.src.services.question_intent_service import QuestionIntentService
from backend.src.services.reranker_service import RerankerService
from backend.src.services.retrieval_pipeline_service import RetrievalPipelineService
from backend.src.services.trust_indicator_service import TrustIndicatorService
from backend.src.services.vague_question_service import VagueQuestionService
from backend.src.utils.article_resolver import resolve_article_number
from shared.schemas.query import AnswerResponse, QueryFilters, QueryRequest


class RagService:
    """Orchestrates hybrid search, reranking, and LLM answer generation."""

    def __init__(self) -> None:
        self._reranker = RerankerService()
        self._pipeline = RetrievalPipelineService(reranker=self._reranker)
        self._trust = TrustIndicatorService()
        self._citations = CitationFormatter()
        self._router = QueryRouterService()
        self._vague = VagueQuestionService()
        self._answer_bundle = AnswerBundleService()
        self._question_intent = QuestionIntentService()
        self._agent = AgentQueryService()

    @property
    def _llm(self) -> LlmService:
        return self._answer_bundle._llm

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]]]:
        if self._vague.is_vague(request.question):
            return self._clarify_response(request, [])
        if AgentQueryService.is_enabled():
            response, chunk_ids, chunks, _explain = await self._agent.query(
                request, history, session,
            )
            self._enrich_citations(response.citations, chunks)
            return response, chunk_ids, chunks
        routed = self._route_request(request)
        results, retrieval_route, explainability = await self._pipeline.retrieve(routed, session=session)
        chunk_ids = [r.get("chunk_id", "") for r in results]
        bundle = await self._answer_bundle.build(request, results, retrieval_route, history)
        self._enrich_citations(bundle["citations"], results)
        effective_route = bundle.get("retrieval_route") or retrieval_route
        response = AnswerResponse(
            answer=bundle["answer_text"],
            conversation_id=request.conversation_id or "",
            citations=bundle["citations"],
            disclaimer=bundle["disclaimer"],
            retrieval_route=effective_route,
            confidence_score=bundle["quality"]["confidence_score"],  # type: ignore[arg-type]
            verification_questions=bundle["quality"]["verification_questions"],  # type: ignore[arg-type]
            retrieval_explainability=explainability,
            coverage_guidance=bundle["coverage_guidance"],
            coverage_status=bundle["coverage_status"],
        )
        return response, chunk_ids, results

    async def query_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        is_layperson = request.audience == "layperson"
        if self._vague.is_vague(request.question):
            bundle = self._build_clarify_bundle(request)
            yield {"step": "search", "message": "Ik heb uw vraag ontvangen..." if is_layperson else "Vraag ontvangen"}
            yield self._complete_event(request, bundle, None, None)
            return
        if AgentQueryService.is_enabled():
            async for event in self._agent.query_with_events(request, history, session):
                yield event
            return
        yield {"step": "search", "message": "Ik bekijk de relevante EU-regels..." if is_layperson else "Zoeken in EU-documenten..."}
        routed = self._route_request(request)
        yield {
            "step": "router",
            "message": "Ik bepaal de juiste juridische zoekroute..." if is_layperson else "Router bepaalt retrievalstrategie...",
            "detail": {"route": routed.filters.model_dump() if routed.filters else {}},
        }
        results, retrieval_route, explainability = await self._pipeline.retrieve(routed, session=session)
        yield {
            "step": "found",
            "message": "Relevante regels gevonden" if is_layperson else f"{len(results)} relevante artikelen gevonden",
            "detail": {
                "count": len(results),
                "audience": request.audience,
                "retrieval_route": retrieval_route,
                "chunk_ids": [r.get("chunk_id", "") for r in results],
                "retrieval_chunks": results,
                "retrieval_explainability": explainability.model_dump(mode="json"),
            },
        }
        consolidated = self._trust.prefer_consolidated(results)
        yield {"step": "versions", "message": "Ik selecteer de meest actuele officiële versies..." if is_layperson else "Meest recente geconsolideerde versies geselecteerd"}
        yield {"step": "generating", "message": "Ik stel een antwoord voor u samen..." if is_layperson else "Antwoord wordt samengesteld..."}
        bundle = await self._answer_bundle.build(request, consolidated, retrieval_route, history)
        self._enrich_citations(bundle["citations"], consolidated)
        effective_route = bundle.get("retrieval_route") or retrieval_route
        yield self._complete_event(request, bundle, effective_route, explainability)

    async def _build_answer_bundle(
        self,
        request: QueryRequest,
        chunks: list[dict[str, Any]],
        retrieval_route: str | None,
        history: list[dict] | None,
    ) -> dict[str, Any]:
        return await self._answer_bundle.build(request, chunks, retrieval_route, history)

    def _complete_event(self, request, bundle, retrieval_route, explainability) -> dict[str, Any]:
        return {
            "step": "complete",
            "message": "Klaar",
            "detail": {
                "answer": bundle["answer_text"],
                "conversation_id": request.conversation_id,
                "citations": [c.model_dump(mode="json") for c in bundle["citations"]],
                "disclaimer": bundle["disclaimer"],
                "retrieval_route": retrieval_route,
                "confidence_score": bundle["quality"]["confidence_score"],
                "verification_questions": bundle["quality"]["verification_questions"],
                "retrieval_explainability": (
                    explainability.model_dump(mode="json") if explainability else None
                ),
                "coverage_guidance": (
                    bundle["coverage_guidance"].model_dump(mode="json")
                    if bundle["coverage_guidance"]
                    else None
                ),
                "coverage_status": bundle["coverage_status"],
            },
        }

    def _build_clarify_bundle(self, request: QueryRequest) -> dict[str, Any]:
        from shared.legal.disclaimers import get_disclaimer

        questions = self._vague.build_questions(request.audience)
        return {
            "answer_text": self._vague.build_answer(request.audience),
            "citations": [],
            "disclaimer": get_disclaimer(request.audience, request.language),  # type: ignore[arg-type]
            "quality": {"confidence_score": 0.0, "verification_questions": questions},
            "coverage_guidance": None,
            "coverage_status": "clarify_only",
        }

    def _clarify_response(
        self,
        request: QueryRequest,
        chunks: list[dict[str, Any]],
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]]]:
        bundle = self._build_clarify_bundle(request)
        response = AnswerResponse(
            answer=bundle["answer_text"],
            conversation_id=request.conversation_id or "",
            citations=[],
            disclaimer=bundle["disclaimer"],
            confidence_score=0.0,
            verification_questions=bundle["quality"]["verification_questions"],  # type: ignore[arg-type]
            coverage_status="clarify_only",
        )
        return response, [], chunks

    def _enrich_citations(self, citations: list, chunks: list[dict]) -> None:
        chunk_map = {chunk.get("celex"): chunk for chunk in chunks}
        for cite in citations:
            chunk = chunk_map.get(cite.celex) or (chunks[0] if chunks else {})
            if not cite.article:
                cite.article = resolve_article_number(chunk)
            self._trust.enrich_citation(cite, chunk)
            cite.legal_citation = self._citations.to_legal_format(cite)
            score = chunk.get("score")
            rerank = chunk.get("rerank_score")
            cite.retrieval_score = float(score) if score is not None else None
            cite.rerank_score = float(rerank) if rerank is not None else None

    def _route_request(self, request: QueryRequest) -> QueryRequest:
        route = self._router.route(request.question, request.language)
        intent = self._question_intent.analyze(request.question)
        existing = request.filters.model_dump() if request.filters else {}
        merged_filters: dict[str, object] = {
            "domain": existing.get("domain") or (route.domains[0] if route.domains else None),
            "doc_type": existing.get("doc_type") or (route.doc_types[0] if route.doc_types else None),
            "celex": existing.get("celex") or route.celex_hint or intent.suggested_celex,
            "language": existing.get("language") or route.language,
            "time_context": existing.get("time_context") or route.time_context,
            "in_force_only": existing.get("in_force_only", route.time_context != "historical"),
            "include_deprecated": existing.get("include_deprecated", False),
            "consolidated_preferred": existing.get("consolidated_preferred", True),
            "intent_id": route.intent_id,
            "router_confidence": route.confidence,
            "domain_cluster": route.domain_cluster,
        }
        return request.model_copy(update={
            "language": route.language,
            "filters": QueryFilters(**merged_filters),
        })
