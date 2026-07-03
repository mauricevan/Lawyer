"""Version conflict detection and retrieval resolution (plan13 AD)."""
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Document
from backend.src.utils.document_version_config import (
    registered_version_families,
    version_gate_policy,
    version_resolution_policy,
)
from backend.src.utils.document_version_utils import (
    chunk_version_type,
    extract_base_celex,
    version_priority_rank,
)
from ingestion.src.data.curated_loader import load_curated_documents
from shared.schemas.query import QueryFilters


@dataclass(slots=True)
class VersionConflictRecord:
    base_celex: str
    language: str
    version_types: tuple[str, ...]
    celex_values: tuple[str, ...]


class DocumentVersionConflictService:
    """Detects multi-version families and resolves retrieval conflicts."""

    def __init__(self) -> None:
        self._resolution = version_resolution_policy()

    async def scan_indexed(self, session: AsyncSession) -> list[VersionConflictRecord]:
        result = await session.execute(select(Document).where(Document.indexed_at.is_not(None)))
        return self._build_conflicts(result.scalars().all())

    def scan_curated(self) -> list[VersionConflictRecord]:
        return self._build_conflicts_from_metadata(load_curated_documents())

    def summarize(self, records: list[VersionConflictRecord]) -> dict[str, Any]:
        return {
            "conflict_count": len(records),
            "families": [
                {
                    "base_celex": row.base_celex,
                    "language": row.language,
                    "version_types": list(row.version_types),
                    "celex_values": list(row.celex_values),
                }
                for row in records
            ],
        }

    def validate_registered_families(self) -> dict[str, Any]:
        curated = {row.base_celex for row in self.scan_curated()}
        registered = {row["base_celex"] for row in registered_version_families()}
        missing = sorted(curated - registered)
        gate = version_gate_policy()
        passed = not missing or not gate.get("require_registered_families", True)
        return {"passed": passed, "missing_registered_families": missing, "registered": sorted(registered)}

    def resolve_retrieval_chunks(
        self,
        chunks: list[dict[str, Any]],
        filters: QueryFilters | None,
    ) -> list[dict[str, Any]]:
        if filters and filters.celex and self._resolution.get("allow_explicit_celex_override", True):
            return chunks
        if not self._resolution.get("exclude_lower_priority_in_default_search", True):
            return chunks
        return self._keep_highest_priority_per_family(chunks)

    def _build_conflicts(self, documents: list[Document]) -> list[VersionConflictRecord]:
        grouped: dict[tuple[str, str], list[Document]] = defaultdict(list)
        for document in documents:
            grouped[(extract_base_celex(document.celex), document.language)].append(document)
        return self._records_from_groups(grouped)

    def _build_conflicts_from_metadata(self, documents) -> list[VersionConflictRecord]:
        grouped: dict[tuple[str, str], list] = defaultdict(list)
        for document in documents:
            grouped[(extract_base_celex(document.celex), document.language)].append(document)
        return self._records_from_groups(grouped)

    def _records_from_groups(self, grouped: dict[tuple[str, str], list]) -> list[VersionConflictRecord]:
        records: list[VersionConflictRecord] = []
        for (base_celex, language), members in grouped.items():
            types = {self._member_version_type(member) for member in members}
            if len(members) < 2 or len(types) < 2:
                continue
            records.append(
                VersionConflictRecord(
                    base_celex=base_celex,
                    language=language,
                    version_types=tuple(sorted(types)),
                    celex_values=tuple(sorted({self._member_celex(member) for member in members})),
                )
            )
        return records

    def _keep_highest_priority_per_family(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for chunk in chunks:
            key = (extract_base_celex(chunk.get("celex", "")), chunk.get("language", "nl"))
            grouped[key].append(chunk)
        output: list[dict[str, Any]] = []
        for family_chunks in grouped.values():
            output.extend(self._select_family_chunks(family_chunks))
        return output

    def _select_family_chunks(self, family_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(family_chunks) == 1:
            return family_chunks
        best_rank = max(version_priority_rank(chunk_version_type(chunk)) for chunk in family_chunks)
        winners = {
            chunk.get("celex")
            for chunk in family_chunks
            if version_priority_rank(chunk_version_type(chunk)) == best_rank
        }
        return [chunk for chunk in family_chunks if chunk.get("celex") in winners]

    @staticmethod
    def _member_version_type(member) -> str:
        value = getattr(member, "version_type", "base")
        return str(getattr(value, "value", value)).lower()

    @staticmethod
    def _member_celex(member) -> str:
        return str(getattr(member, "celex", ""))
