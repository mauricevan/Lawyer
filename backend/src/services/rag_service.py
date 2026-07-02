"""Hybrid RAG retrieval and answer orchestration."""
import logging
import re
from collections.abc import AsyncIterator
from typing import Any

from backend.src.services.embedding_service import get_embedding_service
from backend.src.services.llm_service import LlmService
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.reranker_service import RerankerService
from backend.src.services.trust_indicator_service import TrustIndicatorService
from backend.src.services.citation_formatter import CitationFormatter
from shared.schemas.query import AnswerResponse, QueryRequest

logger = logging.getLogger(__name__)

RETRIEVAL_CANDIDATE_LIMIT = 200

# Lightweight lexical hints to rescue sparse-but-important regulations.
LEGAL_TERM_CELEX_HINTS: dict[str, str] = {
    "dora": "32022R2554",
    "digitale operationele weerbaarheid": "32022R2554",
    "csrd": "32022L2464",
    "duurzaamheidsrapportering": "32022L2464",
}


class RagService:
    """Orchestrates hybrid search, reranking, and LLM answer generation."""

    def __init__(self) -> None:
        self._embeddings = get_embedding_service()
        self._qdrant = QdrantService()
        self._reranker = RerankerService()
        self._llm = LlmService()
        self._trust = TrustIndicatorService()
        self._citations = CitationFormatter()

    async def query(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
    ) -> tuple[AnswerResponse, list[str]]:
        chunk_ids: list[str] = []
        results = await self._retrieve(request)
        chunk_ids = [r.get("chunk_id", "") for r in results]
        answer_text, citations = await self._llm.generate_answer(
            request.question,
            results,
            history,
            request.query_mode,
            request.audience,
        )
        for cite, chunk in zip(citations, results[: len(citations)]):
            self._trust.enrich_citation(cite, chunk)
            cite.legal_citation = self._citations.to_legal_format(cite)
        response = AnswerResponse(
            answer=answer_text,
            conversation_id=request.conversation_id or "",
            citations=citations,
        )
        return response, chunk_ids

    async def query_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        is_layperson = request.audience == "layperson"
        yield {
            "step": "search",
            "message": (
                "Ik bekijk de relevante EU-regels..."
                if is_layperson
                else "Zoeken in EU-documenten..."
            ),
        }
        results = await self._retrieve(request)
        yield {
            "step": "found",
            "message": (
                "Relevante regels gevonden"
                if is_layperson
                else f"{len(results)} relevante artikelen gevonden"
            ),
            "detail": {"count": len(results), "audience": request.audience},
        }
        consolidated = self._trust.prefer_consolidated(results)
        yield {
            "step": "versions",
            "message": (
                "Ik selecteer de meest actuele officiële versies..."
                if is_layperson
                else "Meest recente geconsolideerde versies geselecteerd"
            ),
        }
        yield {
            "step": "generating",
            "message": (
                "Ik stel een antwoord voor u samen..."
                if is_layperson
                else "Antwoord wordt samengesteld..."
            ),
        }
        answer_text, citations = await self._llm.generate_answer(
            request.question,
            consolidated,
            history,
            request.query_mode,
            request.audience,
        )
        for cite, chunk in zip(citations, consolidated[: len(citations)]):
            self._trust.enrich_citation(cite, chunk)
            cite.legal_citation = self._citations.to_legal_format(cite)
        yield {
            "step": "complete",
            "message": "Klaar",
            "detail": {
                "answer": answer_text,
                "conversation_id": request.conversation_id,
                "citations": [c.model_dump(mode="json") for c in citations],
            },
        }

    async def _retrieve(self, request: QueryRequest) -> list[dict[str, Any]]:
        vector = self._embeddings.embed_query(request.question)
        filters = request.filters
        lang = filters.language if filters else request.language
        in_force = filters.in_force_only if filters else True
        dense = self._qdrant.search(
            vector,
            limit=RETRIEVAL_CANDIDATE_LIMIT,
            language=lang,
            in_force_only=in_force,
        )
        bm25 = self._bm25_search(request.question, dense)
        hint_hits = self._hint_search(request.question, lang, in_force)
        merged = self._merge_results(hint_hits, dense, bm25)
        if filters and filters.consolidated_preferred:
            merged = self._trust.prefer_consolidated(merged)
        reranked = self._reranker.rerank(request.question, merged, top_k=8)
        if hint_hits:
            # Preserve explicit legal-term intent chunks (e.g. DORA/CSRD) in final context.
            return self._merge_results(hint_hits, reranked)[:8]
        return reranked

    def _bm25_search(self, query: str, candidates: list[dict]) -> list[dict]:
        celex_match = re.search(r"\b\d{5}[A-Z]\d{4}\b", query)
        if not celex_match:
            return []
        celex = celex_match.group()
        return [c for c in candidates if celex in c.get("celex", "") or celex in c.get("text", "")]

    def _hint_search(
        self,
        query: str,
        language: str | None,
        in_force_only: bool,
    ) -> list[dict]:
        query_lower = query.lower()
        target_celex = {
            celex for hint, celex in LEGAL_TERM_CELEX_HINTS.items() if hint in query_lower
        }
        if not target_celex:
            return []
        return self._qdrant.search_by_celex(
            celex_values=target_celex,
            limit=12,
            language=language,
            in_force_only=in_force_only,
        )

    def _merge_results(self, *result_groups: list[dict]) -> list[dict]:
        seen = set()
        merged = []
        for group in result_groups:
            for result in group:
                cid = result.get("chunk_id")
                if cid and cid not in seen:
                    seen.add(cid)
                    merged.append(result)
        return merged
