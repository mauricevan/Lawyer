"""Async read-only telemetry — snapshot isolation, never mutates user output."""
import asyncio
import logging
import uuid
from typing import Any

from backend.src.config import settings
from backend.src.services.internal_trace_store_service import internal_trace_store
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_explanation import InternalAnalysisTrace, PublishedExplanation

logger = logging.getLogger(__name__)


class InternalAnalysisOrchestrator:
    """Fire-and-forget observers on deep-copied published snapshots."""

    def spawn(
        self,
        published: PublishedExplanation,
        analysis: LegalCaseAnalysis | None,
    ) -> None:
        if not settings.internal_simulation_telemetry_enabled:
            return
        snapshot = published.model_copy(deep=True)
        asyncio.create_task(
            self._run(snapshot, analysis),
            name=f"telemetry-{snapshot.draft.retrieval_context_id[:8]}",
        )

    async def _run(
        self,
        published: PublishedExplanation,
        analysis: LegalCaseAnalysis | None,
    ) -> InternalAnalysisTrace:
        trace_id = str(uuid.uuid4())
        try:
            payload = self._collect_readonly(published, analysis)
            logger.debug("internal_trace %s stored keys=%s", trace_id, list(payload.keys()))
        except Exception as exc:
            logger.warning("telemetry failed trace_id=%s: %s", trace_id, exc)
            payload = {}
        trace = InternalAnalysisTrace(
            trace_id=trace_id,
            source_context_id=published.draft.retrieval_context_id,
            **payload,
        )
        internal_trace_store.put(trace)
        return trace

    def _collect_readonly(
        self,
        published: PublishedExplanation,
        analysis: LegalCaseAnalysis | None,
    ) -> dict[str, Any]:
        """Optional V7–V10 hooks — read snapshot only; no answer mutation."""
        _ = published, analysis
        return {}
