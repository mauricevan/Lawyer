"""Document index staleness detection (plan13 AA)."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Document
from backend.src.utils.document_lifecycle_config import load_document_lifecycle_policy, scan_gates, staleness_thresholds


@dataclass(slots=True)
class StalenessRecord:
    celex: str
    language: str
    status: str
    indexed_at: datetime | None
    modified_at: datetime | None
    index_age_hours: float | None
    modified_drift_hours: float | None


class DocumentStalenessService:
    """Scans documents for index freshness drift."""

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now or datetime.now(timezone.utc)
        self._thresholds = staleness_thresholds()

    async def scan(self, session: AsyncSession) -> list[StalenessRecord]:
        result = await session.execute(select(Document))
        documents = result.scalars().all()
        return [self._classify(document) for document in documents]

    def summarize(self, records: list[StalenessRecord]) -> dict[str, Any]:
        counts = {status: 0 for status in ("fresh", "stale", "critical", "never_indexed")}
        for record in records:
            counts[record.status] = counts.get(record.status, 0) + 1
        return {
            "total_documents": len(records),
            "fresh": counts.get("fresh", 0),
            "stale": counts.get("stale", 0),
            "critical": counts.get("critical", 0),
            "never_indexed": counts.get("never_indexed", 0),
            "scanned_at": self._now.isoformat(),
        }

    def evaluate_gates(self, summary: dict[str, Any]) -> dict[str, Any]:
        gates = scan_gates()
        failures: list[str] = []
        checks = (
            ("never_indexed", "max_never_indexed"),
            ("critical", "max_critical"),
            ("stale", "max_stale"),
        )
        for metric, gate_key in checks:
            limit = gates.get(gate_key)
            if limit is None:
                continue
            value = int(summary.get(metric, 0))
            if value > limit:
                failures.append(f"{metric} {value} exceeds {gate_key}={limit}")
        return {"passed": not failures, "failures": failures, "gates": gates}

    def _classify(self, document: Document) -> StalenessRecord:
        indexed_at = self._as_utc(document.indexed_at)
        modified_at = self._as_utc(document.modified_at)
        if indexed_at is None:
            return self._record(document, "never_indexed", None, None)
        index_age = self._hours_between(indexed_at, self._now)
        drift = self._hours_between(indexed_at, modified_at) if modified_at else None
        if self._is_modified_drift(indexed_at, modified_at):
            status = "critical" if drift and drift > self._critical_hours() else "stale"
            return self._record(document, status, index_age, drift)
        if index_age > self._critical_hours():
            return self._record(document, "critical", index_age, drift)
        if index_age > self._warning_hours():
            return self._record(document, "stale", index_age, drift)
        return self._record(document, "fresh", index_age, drift)

    def _record(
        self,
        document: Document,
        status: str,
        index_age: float | None,
        drift: float | None,
    ) -> StalenessRecord:
        return StalenessRecord(
            celex=document.celex,
            language=document.language,
            status=status,
            indexed_at=self._as_utc(document.indexed_at),
            modified_at=self._as_utc(document.modified_at),
            index_age_hours=index_age,
            modified_drift_hours=drift,
        )

    def _is_modified_drift(self, indexed_at: datetime, modified_at: datetime | None) -> bool:
        if not self._thresholds.get("modified_drift_is_stale", True):
            return False
        return modified_at is not None and modified_at > indexed_at

    def _warning_hours(self) -> float:
        return float(self._thresholds.get("max_index_age_hours", 168))

    def _critical_hours(self) -> float:
        return float(self._thresholds.get("critical_index_age_hours", 720))

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

    @staticmethod
    def report_path() -> str:
        policy = load_document_lifecycle_policy()
        return str(policy.get("report", {}).get("path", "docs/data/lifecycle-reports/staleness-latest.json"))
