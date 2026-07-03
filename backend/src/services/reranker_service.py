"""Cross-encoder reranking for retrieved chunks."""
import logging
import time
from typing import Any, Callable

from backend.src.config import settings
from backend.src.utils.reranker_config import load_reranker_config, resolve_model_id

logger = logging.getLogger(__name__)


class RerankerService:
    """Reranks retrieved chunks by query relevance."""

    def __init__(
        self,
        variant: str | None = None,
        model: Any | None = None,
        model_factory: Callable[[str], Any] | None = None,
    ) -> None:
        config = load_reranker_config()
        self._variant = variant or settings.reranker_variant
        self._model_id = resolve_model_id(self._variant)
        self._model = model
        self._model_factory = model_factory
        self._default_variant = str(config.get("default_variant", "control"))
        self.last_latency_ms: float = 0.0

    @property
    def variant(self) -> str:
        return self._variant

    @property
    def model_id(self) -> str:
        return self._model_id

    def rerank(self, query: str, results: list[dict[str, Any]], top_k: int | None = None) -> list[dict[str, Any]]:
        if not results:
            self.last_latency_ms = 0.0
            return []
        limit = top_k or settings.rerank_top_k
        candidates = results[: settings.rerank_candidate_limit]
        started = time.perf_counter()
        try:
            ranked = self._rerank_cross_encoder(query, candidates, limit)
        except Exception as exc:
            logger.warning("Reranker fallback to score order: %s", exc)
            ranked = candidates[:limit]
        self.last_latency_ms = (time.perf_counter() - started) * 1000
        return ranked

    def _rerank_cross_encoder(
        self, query: str, results: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        model = self._get_model()
        pairs = [(query, r.get("text", "")) for r in results]
        scores = model.predict(pairs)
        scored = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
        return [r for r, _ in scored[:top_k]]

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        if self._model_factory is not None:
            self._model = self._model_factory(self._model_id)
            return self._model
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self._model_id)
        return self._model
