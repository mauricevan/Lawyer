"""In-memory store for async explanation telemetry traces (admin-only)."""
from collections import deque
from threading import Lock

from shared.schemas.legal_explanation import InternalAnalysisTrace

_MAX_TRACES = 200


class InternalTraceStoreService:
    """Ring buffer of read-only internal analysis traces."""

    def __init__(self, max_traces: int = _MAX_TRACES) -> None:
        self._traces: deque[InternalAnalysisTrace] = deque(maxlen=max_traces)
        self._lock = Lock()

    def put(self, trace: InternalAnalysisTrace) -> None:
        with self._lock:
            self._traces.append(trace)

    def get(self, trace_id: str) -> InternalAnalysisTrace | None:
        with self._lock:
            return next((item for item in self._traces if item.trace_id == trace_id), None)

    def list_recent(self, limit: int = 20) -> list[InternalAnalysisTrace]:
        capped = max(1, min(limit, _MAX_TRACES))
        with self._lock:
            return list(self._traces)[-capped:]


internal_trace_store = InternalTraceStoreService()
