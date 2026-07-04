"""CELEX hint search and discovery bootstrap for retrieval pipeline."""
from backend.src.services.document_deprecation_service import DocumentDeprecationService
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.retrieval_explainability_service import DiscoveryContext
from backend.src.utils.celex_hint_resolver import merge_discovery_celex_set
from backend.src.utils.qdrant_resilience import safe_celex_hint_search
from shared.schemas.query import QueryFilters


def build_discovery_context(candidates: list) -> DiscoveryContext:
    if not candidates:
        return DiscoveryContext()
    top = candidates[0]
    return DiscoveryContext(celex=top.celex, source=top.source)


def hint_search(
    qdrant: QdrantService,
    deprecation: DocumentDeprecationService,
    question: str,
    language: str | None,
    in_force_only: bool,
    filters: QueryFilters | None,
) -> list[dict]:
    target_celex = merge_discovery_celex_set(question)
    if not target_celex:
        return []
    if filters and filters.celex:
        target_celex = {filters.celex}
    else:
        target_celex = deprecation.filter_celex_hints(target_celex, filters)
    if not target_celex:
        return []
    return safe_celex_hint_search(qdrant, target_celex, language, in_force_only)
