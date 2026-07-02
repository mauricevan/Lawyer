"""Prometheus metric definitions and exposition helpers."""

PROMETHEUS_AVAILABLE = False
CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

try:
    from prometheus_client import CONTENT_TYPE_LATEST as _CONTENT_TYPE
    from prometheus_client import Counter as _Counter
    from prometheus_client import generate_latest as _generate_latest

    PROMETHEUS_AVAILABLE = True
    CONTENT_TYPE_LATEST = _CONTENT_TYPE
except ImportError:
    _Counter = None
    _generate_latest = None


class _NoopMetric:
    def labels(self, **_kwargs: str) -> "_NoopMetric":
        return self

    def inc(self, _amount: float = 1) -> None:
        return None


def _counter(name: str, description: str, labels: list[str] | None = None) -> _NoopMetric | object:
    if not PROMETHEUS_AVAILABLE or _Counter is None:
        return _NoopMetric()
    return _Counter(name, description, labels or [])


QUERY_TOTAL = _counter("lawyer_queries_total", "Total query requests processed", ["mode"])
CACHE_HITS_TOTAL = _counter("lawyer_cache_hits_total", "Retrieval cache hits")
FALLBACK_ATTEMPTS_TOTAL = _counter("lawyer_fallback_attempts_total", "Live fallback attempts")
FALLBACK_SUCCESS_TOTAL = _counter("lawyer_fallback_success_total", "Successful live fallbacks")
INJECTION_FLAGS_TOTAL = _counter("lawyer_injection_flags_total", "Prompt injection detections")
AUTO_UPGRADE_QUEUED_TOTAL = _counter("lawyer_auto_upgrade_queued_total", "Auto-upgrade ingest jobs queued")
INGEST_ENQUEUE_TOTAL = _counter(
    "lawyer_ingest_enqueue_total",
    "Ingestion tasks enqueued to worker",
    ["result"],
)
RETRIEVAL_ROUTE_TOTAL = _counter(
    "lawyer_retrieval_route_total",
    "Retrieval route usage",
    ["route"],
)


def export_prometheus() -> tuple[bytes, str]:
    """Return Prometheus exposition payload and content type."""
    if not PROMETHEUS_AVAILABLE or _generate_latest is None:
        return b"", CONTENT_TYPE_LATEST
    return _generate_latest(), CONTENT_TYPE_LATEST
