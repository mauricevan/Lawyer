"""Estimate answer confidence from retrieval signals."""
LOW_CONFIDENCE_THRESHOLD = 0.35
LIVE_FALLBACK_PENALTY = 0.12
NO_CITATION_PENALTY = 0.2


class AnswerConfidenceService:
    """Scores how strongly retrieval supports the generated answer."""

    def assess(
        self,
        chunks: list[dict],
        retrieval_route: str | None,
        citation_count: int,
    ) -> float:
        if not chunks:
            return 0.0
        scores = [float(chunk.get("score", 0.0)) for chunk in chunks]
        base = max(scores, default=0.0)
        if retrieval_route == "live_fallback":
            base -= LIVE_FALLBACK_PENALTY
        if citation_count == 0:
            base -= NO_CITATION_PENALTY
        return round(min(1.0, max(0.0, base)), 3)

    def is_low(self, score: float) -> bool:
        return score < LOW_CONFIDENCE_THRESHOLD
