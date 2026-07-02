"""In-process operational counters for query and retrieval paths."""
from dataclasses import dataclass, field

from backend.src.services import prometheus_exporter as prom


@dataclass
class MetricsService:
    """Tracks high-level runtime counters for admin dashboards."""

    query_total: int = 0
    stream_query_total: int = 0
    cache_hits: int = 0
    fallback_attempts: int = 0
    fallback_successes: int = 0
    injection_flags: int = 0
    auto_upgrade_queued: int = 0
    retrieval_routes: dict[str, int] = field(default_factory=dict)

    def record_query(self, is_stream: bool = False) -> None:
        mode = "stream" if is_stream else "sync"
        prom.QUERY_TOTAL.labels(mode=mode).inc()
        if is_stream:
            self.stream_query_total += 1
        else:
            self.query_total += 1

    def record_cache_hit(self) -> None:
        prom.CACHE_HITS_TOTAL.inc()
        self.cache_hits += 1

    def record_fallback(self, succeeded: bool) -> None:
        prom.FALLBACK_ATTEMPTS_TOTAL.inc()
        self.fallback_attempts += 1
        if succeeded:
            prom.FALLBACK_SUCCESS_TOTAL.inc()
            self.fallback_successes += 1

    def record_route(self, route: str | None) -> None:
        if not route:
            return
        prom.RETRIEVAL_ROUTE_TOTAL.labels(route=route).inc()
        self.retrieval_routes[route] = self.retrieval_routes.get(route, 0) + 1

    def record_injection_flag(self) -> None:
        prom.INJECTION_FLAGS_TOTAL.inc()
        self.injection_flags += 1

    def record_auto_upgrade(self) -> None:
        prom.AUTO_UPGRADE_QUEUED_TOTAL.inc()
        self.auto_upgrade_queued += 1

    def snapshot(self) -> dict[str, object]:
        return {
            "query_total": self.query_total,
            "stream_query_total": self.stream_query_total,
            "cache_hits": self.cache_hits,
            "fallback_attempts": self.fallback_attempts,
            "fallback_successes": self.fallback_successes,
            "injection_flags": self.injection_flags,
            "auto_upgrade_queued": self.auto_upgrade_queued,
            "retrieval_routes": self.retrieval_routes,
        }


metrics_service = MetricsService()
