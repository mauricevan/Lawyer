"""Hybrid RAG retrieval and answer orchestration."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.answer_policy_service import AnswerPolicyService
from backend.src.services.answer_quality_service import answer_quality_service
from backend.src.services.citation_formatter import CitationFormatter
from backend.src.services.llm_service import LlmService
from backend.src.services.query_router_service import QueryRouterService
from backend.src.services.reranker_service import RerankerService
from backend.src.services.retrieval_pipeline_service import RetrievalPipelineService
from backend.src.services.source_consistency_service import SourceConsistencyService
from backend.src.services.trust_indicator_service import TrustIndicatorService
from shared.schemas.query import AnswerResponse, QueryFilters, QueryRequest


class RagService:
    """Orchestrates hybrid search, reranking, and LLM answer generation."""

    def __init__(self) -> None:
        self._reranker = RerankerService()
        self._pipeline = RetrievalPipelineService(reranker=self._reranker)
        self._llm = LlmService()
        self._trust = TrustIndicatorService()
        self._citations = CitationFormatter()
        self._router = QueryRouterService()
        self._source_consistency = SourceConsistencyService()
        self._answer_policy = AnswerPolicyService()

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> tuple[AnswerResponse, list[str], list[dict[str, Any]]]:
        routed = self._route_request(request)
        results, retrieval_route, explainability = await self._pipeline.retrieve(routed, session=session)
        chunk_ids = [r.get("chunk_id", "") for r in results]
        answer_text, citations = await self._llm.generate_answer(
            request.question, results, history, request.query_mode, request.audience,
        )
        citations = self._source_consistency.filter_citations(citations, results)
        query_language = routed.filters.language if routed.filters else routed.language
        answer_text, citations, disclaimer = self._answer_policy.finalize_answer(
            answer_text, citations, results, request.audience, query_language or "nl",
        )
        self._enrich_citations(citations, results)
        quality = answer_quality_service.package(request, results, retrieval_route, len(citations))
        response = AnswerResponse(
            answer=answer_text,
            conversation_id=request.conversation_id or "",
            citations=citations,
            disclaimer=disclaimer,
            retrieval_route=retrieval_route,
            confidence_score=quality["confidence_score"],  # type: ignore[arg-type]
            verification_questions=quality["verification_questions"],  # type: ignore[arg-type]
            retrieval_explainability=explainability,
        )
        return response, chunk_ids, results

    async def query_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
        session: AsyncSession | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        is_layperson = request.audience == "layperson"
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
        answer_text, citations = await self._llm.generate_answer(
            request.question, consolidated, history, request.query_mode, request.audience,
        )
        citations = self._source_consistency.filter_citations(citations, consolidated)
        query_language = routed.filters.language if routed.filters else routed.language
        answer_text, citations, disclaimer = self._answer_policy.finalize_answer(
            answer_text, citations, consolidated, request.audience, query_language or "nl",
        )
        self._enrich_citations(citations, consolidated)
        quality = answer_quality_service.package(request, consolidated, retrieval_route, len(citations))
        yield {
            "step": "complete",
            "message": "Klaar",
            "detail": {
                "answer": answer_text,
                "conversation_id": request.conversation_id,
                "citations": [c.model_dump(mode="json") for c in citations],
                "disclaimer": disclaimer,
                "retrieval_route": retrieval_route,
                "confidence_score": quality["confidence_score"],
                "verification_questions": quality["verification_questions"],
                "retrieval_explainability": explainability.model_dump(mode="json"),
            },
        }

    async def _retrieve(
        self,
        request: QueryRequest,
        session: AsyncSession | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        results, route, _ = await self._pipeline.retrieve(request, session=session)
        return results, route

    def _enrich_citations(self, citations: list, chunks: list[dict]) -> None:
        chunk_map = {chunk.get("celex"): chunk for chunk in chunks}
        for cite in citations:
            chunk = chunk_map.get(cite.celex) or (chunks[0] if chunks else {})
            self._trust.enrich_citation(cite, chunk)
            cite.legal_citation = self._citations.to_legal_format(cite)
            score = chunk.get("score")
            rerank = chunk.get("rerank_score")
            cite.retrieval_score = float(score) if score is not None else None
            cite.rerank_score = float(rerank) if rerank is not None else None

    def _route_request(self, request: QueryRequest) -> QueryRequest:
        route = self._router.route(request.question, request.language)
        existing = request.filters.model_dump() if request.filters else {}
        merged_filters: dict[str, object] = {
            "domain": existing.get("domain") or (route.domains[0] if route.domains else None),
            "doc_type": existing.get("doc_type") or (route.doc_types[0] if route.doc_types else None),
            "celex": existing.get("celex") or route.celex_hint,
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
