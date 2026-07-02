"""Track citation coverage and confidence across queries."""
from dataclasses import dataclass, field


@dataclass
class CitationReliabilityService:
    """In-process counters for release-level citation quality monitoring."""

    query_total: int = 0
    with_citations: int = 0
    low_confidence_total: int = 0
    route_counts: dict[str, int] = field(default_factory=dict)

    def record(self, citation_count: int, confidence: float, route: str | None) -> None:
        self.query_total += 1
        if citation_count > 0:
            self.with_citations += 1
        if confidence < 0.35:
            self.low_confidence_total += 1
        if route:
            self.route_counts[route] = self.route_counts.get(route, 0) + 1

    def snapshot(self) -> dict[str, object]:
        total = self.query_total or 1
        return {
            "query_total": self.query_total,
            "citation_coverage_rate": round(self.with_citations / total, 4),
            "low_confidence_rate": round(self.low_confidence_total / total, 4),
            "retrieval_routes": self.route_counts,
        }


citation_reliability_service = CitationReliabilityService()
