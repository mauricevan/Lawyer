"""Build retrieval explainability payloads for API responses."""
from dataclasses import dataclass

from backend.src.services.reranker_service import RerankerService
from shared.schemas.query import QueryFilters, QueryRequest
from shared.schemas.retrieval_explainability import (
    RetrievalExplainability,
    RouterDecision,
    SourceScoreBreakdown,
)


@dataclass(slots=True)
class StageCounts:
    dense: int = 0
    hints: int = 0
    bm25: int = 0
    pg: int = 0
    merged: int = 0
    final: int = 0


@dataclass(slots=True)
class DiscoveryContext:
    celex: str | None = None
    source: str | None = None
    live_fallback_forced: bool = False


class RetrievalExplainabilityService:
    """Maps internal retrieval context to public explainability schema."""

    def build(
        self,
        route: str,
        request: QueryRequest,
        counts: StageCounts,
        reranker: RerankerService,
        hybrid_rrf_enabled: bool,
        chunks: list[dict],
        discovery: DiscoveryContext | None = None,
    ) -> RetrievalExplainability:
        filters = request.filters or QueryFilters()
        ctx = discovery or DiscoveryContext()
        return RetrievalExplainability(
            route=route,  # type: ignore[arg-type]
            query_language=filters.language or request.language,
            router=RouterDecision(
                domains=[filters.domain] if filters.domain else [],
                doc_types=[filters.doc_type] if filters.doc_type else [],
                celex_hint=filters.celex or ctx.celex,
                language=filters.language or request.language,
                time_context=filters.time_context,
                intent_id=filters.intent_id,
                confidence=filters.router_confidence,
                domain_cluster=filters.domain_cluster,
            ),
            reranker_variant=reranker.variant,
            rerank_latency_ms=reranker.last_latency_ms,
            hybrid_rrf_enabled=hybrid_rrf_enabled,
            stage_counts={
                "dense": counts.dense,
                "hints": counts.hints,
                "bm25": counts.bm25,
                "pg": counts.pg,
                "merged": counts.merged,
                "final": counts.final,
            },
            sources=self._source_breakdown(chunks),
            discovery_celex=ctx.celex,
            discovery_source=ctx.source,
            live_fallback_forced=ctx.live_fallback_forced,
            chunk_count=len(chunks),
        )

    def _source_breakdown(self, chunks: list[dict]) -> list[SourceScoreBreakdown]:
        output: list[SourceScoreBreakdown] = []
        for chunk in chunks[:8]:
            score = chunk.get("score")
            rerank = chunk.get("rerank_score")
            output.append(SourceScoreBreakdown(
                chunk_id=str(chunk.get("chunk_id", "")),
                celex=str(chunk.get("celex", "")),
                vector_score=float(score) if score is not None else None,
                rerank_score=float(rerank) if rerank is not None else None,
            ))
        return output
