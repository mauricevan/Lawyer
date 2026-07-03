"""Registry-driven document deprecation for retrieval (plan13 AC)."""
from typing import Any

from backend.src.utils.document_deprecation_config import (
    DeprecationEntry,
    deprecation_policy,
    load_deprecation_entries,
)
from shared.schemas.query import QueryFilters

SEARCH_EXCLUDED_STATUSES = frozenset({"soft_deprecated", "retired"})


class DocumentDeprecationService:
    """Applies deprecation register rules to retrieval."""

    def __init__(self) -> None:
        self._policy = deprecation_policy()

    def entries(self) -> tuple[DeprecationEntry, ...]:
        return load_deprecation_entries()

    def summarize(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for entry in self.entries():
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return {
            "registered": len(self.entries()),
            "by_status": counts,
            "search_excluded_celex": sorted(self.excluded_celex()),
        }

    def excluded_celex(self, language: str | None = None) -> set[str]:
        output: set[str] = set()
        for entry in self.entries():
            if entry.status not in SEARCH_EXCLUDED_STATUSES:
                continue
            if entry.language and language and entry.language != language:
                continue
            output.add(entry.celex)
        return output

    def excluded_celex_for_filters(self, filters: QueryFilters | None, language: str | None) -> set[str]:
        if not self._policy.get("default_exclude_from_search", True):
            return set()
        if filters and filters.include_deprecated:
            return set()
        if filters and filters.celex:
            return set()
        return self.excluded_celex(language)

    def filter_celex_hints(self, celex_values: set[str], filters: QueryFilters | None) -> set[str]:
        if not celex_values:
            return celex_values
        return {celex for celex in celex_values if not self.is_excluded(celex, None, filters)}

    def filter_chunks(
        self,
        chunks: list[dict[str, Any]],
        filters: QueryFilters | None,
    ) -> list[dict[str, Any]]:
        return [
            chunk
            for chunk in chunks
            if not self.is_excluded(chunk.get("celex", ""), chunk.get("language"), filters)
        ]

    def is_excluded(self, celex: str, language: str | None, filters: QueryFilters | None) -> bool:
        if not celex:
            return False
        if filters and filters.include_deprecated:
            return False
        if filters and filters.celex and filters.celex == celex:
            if self._policy.get("allow_explicit_celex_lookup", True):
                return False
        entry = self._match_entry(celex, language)
        if entry is None:
            return False
        return entry.status in SEARCH_EXCLUDED_STATUSES

    def _match_entry(self, celex: str, language: str | None) -> DeprecationEntry | None:
        for entry in self.entries():
            if entry.celex != celex:
                continue
            if entry.language and language and entry.language != language:
                continue
            return entry
        return None
