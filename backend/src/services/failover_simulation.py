"""In-process dependency failure simulators (plan14 AB)."""
from typing import Any

from backend.src.services.rag_service import RagService


class QdrantUnavailableSimulator:
    """Simulates empty Qdrant responses."""

    def search(self, *args, **kwargs) -> list[dict[str, Any]]:
        return []

    def search_by_celex(self, *args, **kwargs) -> list[dict[str, Any]]:
        return []

    def search_with_language_fallback(self, *args, **kwargs) -> list[dict[str, Any]]:
        return self.search(*args, **kwargs)

    def search_by_celex_with_language_fallback(self, *args, **kwargs) -> list[dict[str, Any]]:
        return self.search_by_celex(*args, **kwargs)


class QdrantErrorSimulator(QdrantUnavailableSimulator):
    """Simulates hard Qdrant connection failures."""

    def search_with_language_fallback(self, *args, **kwargs) -> list[dict[str, Any]]:
        raise ConnectionError("simulated qdrant outage")


class LiveFallbackSimulator:
    """Returns deterministic live-fallback chunks."""

    async def fallback_chunks(
        self,
        question: str,
        language: str = "nl",
        celex_hint: str | None = None,
        is_celex_allowed=None,
    ):
        return [{
            "chunk_id": "live:32022R2554",
            "celex": "32022R2554",
            "title": "DORA",
            "text": "live excerpt",
            "source": "live_fallback",
        }]


class LowScoreReranker:
    variant = "control"
    model_id = "test"
    last_latency_ms = 0.0

    def rerank(self, *args, **kwargs) -> list[dict[str, Any]]:
        return [{"chunk_id": "local:1", "score": 0.05, "text": "weak local"}]


class EmptyReranker(LowScoreReranker):
    def rerank(self, *args, **kwargs) -> list[dict[str, Any]]:
        return []


class DisabledLiveFlags:
    def is_live_fallback_enabled(self) -> bool:
        return False

    def is_hybrid_rrf_enabled(self) -> bool:
        return True

    def is_auto_upgrade_enabled(self) -> bool:
        return False

    def is_audit_logging_enabled(self) -> bool:
        return False


def apply_failover_scenario(rag: RagService, scenario: dict[str, Any]) -> None:
    """Patch RagService pipeline for a named failure simulation."""
    simulate = scenario.get("simulate", "qdrant_empty")
    if simulate == "qdrant_error":
        rag._pipeline._qdrant = QdrantErrorSimulator()
    else:
        rag._pipeline._qdrant = QdrantUnavailableSimulator()
    reranker = LowScoreReranker() if simulate == "qdrant_low_score" else EmptyReranker()
    rag._pipeline._reranker = reranker
    rag._pipeline._live = LiveFallbackSimulator()
    if scenario.get("live_fallback_enabled") is False:
        rag._pipeline._flags = DisabledLiveFlags()
