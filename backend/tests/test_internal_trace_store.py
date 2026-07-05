"""Tests for admin explanation trace store."""
from shared.schemas.legal_explanation import InternalAnalysisTrace

from backend.src.services.internal_trace_store_service import InternalTraceStoreService


def test_store_and_get_trace() -> None:
    store = InternalTraceStoreService(max_traces=5)
    trace = InternalAnalysisTrace(trace_id="t-1", source_context_id="ctx-1")
    store.put(trace)
    loaded = store.get("t-1")
    assert loaded is not None
    assert loaded.source_context_id == "ctx-1"


def test_list_recent_returns_newest_first_slice() -> None:
    store = InternalTraceStoreService(max_traces=10)
    for index in range(3):
        store.put(InternalAnalysisTrace(trace_id=f"t-{index}", source_context_id=f"ctx-{index}"))
    items = store.list_recent(limit=2)
    assert len(items) == 2
    assert items[-1].trace_id == "t-2"
