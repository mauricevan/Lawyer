"""Automated reindex candidate selection (plan13 AB)."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Document
from backend.src.utils.document_lifecycle_config import reindex_policy


@dataclass(slots=True)
class ReindexCandidate:
    celex: str
    language: str
    reason: str
    indexed_at: datetime | None
    modified_at: datetime | None
    drift_hours: float | None


class DocumentReindexService:
    """Selects documents that require purge-and-reingest."""

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now or datetime.now(timezone.utc)
        self._policy = reindex_policy()

    async def list_candidates(self, session: AsyncSession) -> list[ReindexCandidate]:
        result = await session.execute(select(Document))
        documents = result.scalars().all()
        candidates = [self._candidate(document) for document in documents]
        return [candidate for candidate in candidates if candidate is not None]

    def candidate_key(self, candidate: ReindexCandidate) -> str:
        return f"{candidate.celex}:{candidate.language}"

    def evaluate_sla(self, candidates: list[ReindexCandidate]) -> dict[str, Any]:
        sla_hours = float(self._policy.get("sla_hours", 72))
        violations: list[dict[str, Any]] = []
        for candidate in candidates:
            if candidate.reason != "modified_drift" or candidate.modified_at is None:
                continue
            age = self._hours_since(candidate.modified_at)
            if age > sla_hours:
                violations.append(
                    {
                        "celex": candidate.celex,
                        "language": candidate.language,
                        "drift_age_hours": age,
                        "sla_hours": sla_hours,
                    }
                )
        return {
            "sla_hours": sla_hours,
            "violation_count": len(violations),
            "violations": violations,
            "passed": not violations,
        }

    def _candidate(self, document: Document) -> ReindexCandidate | None:
        reason = self.reindex_reason(document)
        if reason is None:
            return None
        indexed_at = self._as_utc(document.indexed_at)
        modified_at = self._as_utc(document.modified_at)
        drift = self._hours_between(indexed_at, modified_at) if indexed_at and modified_at else None
        return ReindexCandidate(
            celex=document.celex,
            language=document.language,
            reason=reason,
            indexed_at=indexed_at,
            modified_at=modified_at,
            drift_hours=drift,
        )

    def reindex_reason(self, document: Document) -> str | None:
        indexed_at = self._as_utc(document.indexed_at)
        modified_at = self._as_utc(document.modified_at)
        if indexed_at is None and self._policy.get("trigger_on_never_indexed", True):
            return "never_indexed"
        if (
            indexed_at is not None
            and modified_at is not None
            and modified_at > indexed_at
            and self._policy.get("trigger_on_modified_drift", True)
        ):
            return "modified_drift"
        return None

    def _hours_since(self, moment: datetime) -> float:
        return max((self._now - moment).total_seconds() / 3600, 0.0)

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _hours_between(earlier: datetime, later: datetime | None) -> float | None:
        if later is None:
            return None
        return max((later - earlier).total_seconds() / 3600, 0.0)
