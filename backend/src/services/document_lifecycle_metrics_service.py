"""Aggregated document lifecycle metrics for admin (plan13 AD)."""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Document
from backend.src.services.document_deprecation_service import DocumentDeprecationService
from backend.src.services.document_staleness_service import DocumentStalenessService
from backend.src.services.document_version_conflict_service import DocumentVersionConflictService
from ingestion.src.data.curated_loader import load_curated_documents


class DocumentLifecycleMetricsService:
    """Builds unified lifecycle metrics for admin and gates."""

    def __init__(self) -> None:
        self._staleness = DocumentStalenessService()
        self._deprecation = DocumentDeprecationService()
        self._versions = DocumentVersionConflictService()

    async def build_summary(self, session: AsyncSession) -> dict[str, Any]:
        staleness_records = await self._staleness.scan(session)
        version_conflicts = await self._versions.scan_indexed(session)
        coverage = await self._coverage_metrics(session)
        return {
            "staleness": self._staleness.summarize(staleness_records),
            "deprecation": self._deprecation.summarize(),
            "version_conflicts": self._versions.summarize(version_conflicts),
            "coverage": coverage,
            "gate": self._staleness.evaluate_gates(self._staleness.summarize(staleness_records)),
        }

    async def _coverage_metrics(self, session: AsyncSession) -> dict[str, Any]:
        curated_total = len(load_curated_documents())
        indexed = await session.execute(
            select(func.count()).select_from(Document).where(Document.indexed_at.is_not(None))
        )
        indexed_count = int(indexed.scalar() or 0)
        pct = round((indexed_count / curated_total) * 100, 2) if curated_total else 0.0
        return {
            "curated_total": curated_total,
            "indexed_count": indexed_count,
            "coverage_pct": pct,
        }
