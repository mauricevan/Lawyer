"""Tests for retrieval explainability builder."""
from backend.src.services.reranker_service import RerankerService
from backend.src.services.retrieval_explainability_service import (
    RetrievalExplainabilityService,
    StageCounts,
)
from shared.schemas.query import QueryFilters, QueryRequest


class _FakeReranker(RerankerService):
    def __init__(self) -> None:
        super().__init__(variant="control", model=object())
        self.last_latency_ms = 12.5


def test_build_explainability_includes_scores_and_router() -> None:
    service = RetrievalExplainabilityService()
    request = QueryRequest(
        question="Wat is DORA?",
        filters=QueryFilters(domain="finance", language="nl", time_context="current"),
    )
    chunks = [{"chunk_id": "c1", "celex": "32022R2554", "score": 0.91, "rerank_score": 0.88}]
    explainability = service.build(
        "hybrid",
        request,
        StageCounts(dense=20, hints=2, bm25=10, merged=25, final=1),
        _FakeReranker(),
        True,
        chunks,
    )
    assert explainability.route == "hybrid"
    assert explainability.router.domains == ["finance"]
    assert explainability.reranker_variant == "control"
    assert explainability.sources[0].vector_score == 0.91
    assert explainability.sources[0].rerank_score == 0.88
