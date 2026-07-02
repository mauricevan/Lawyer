"""Cross-encoder reranking for retrieved chunks."""
import logging
from typing import Any

from backend.src.config import settings

logger = logging.getLogger(__name__)


class RerankerService:
    """Reranks retrieved chunks by query relevance."""

    def __init__(self) -> None:
        self._model = None

    def rerank(self, query: str, results: list[dict[str, Any]], top_k: int | None = None) -> list[dict[str, Any]]:
        if not results:
            return []
        limit = top_k or settings.rerank_top_k
        candidates = results[: settings.rerank_candidate_limit]
        try:
            return self._rerank_cross_encoder(query, candidates, limit)
        except Exception as exc:
            logger.warning("Reranker fallback to score order: %s", exc)
            return candidates[:limit]

    def _rerank_cross_encoder(
        self, query: str, results: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        model = self._get_model()
        pairs = [(query, r.get("text", "")) for r in results]
        scores = model.predict(pairs)
        scored = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
        return [r for r, _ in scored[:top_k]]

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        return self._model
