"""Post-retrieval chunk filters for domain and document type."""
from backend.src.utils.qdrant_filters import doc_type_matches_celex
from ingestion.src.data.domain_registry_loader import get_domain_keywords
from shared.schemas.query import QueryFilters

DOMAIN_KEYWORDS = get_domain_keywords()


def apply_retrieval_post_filters(
    chunks: list[dict],
    filters: QueryFilters | None,
) -> list[dict]:
    if not filters:
        return chunks
    output = chunks
    if filters.doc_type:
        output = [c for c in output if doc_type_matches_celex(filters.doc_type, c.get("celex", ""))]
    if filters.domain:
        terms = DOMAIN_KEYWORDS.get(filters.domain, ())
        output = [c for c in output if _matches_domain(c, terms)]
    return output


def _matches_domain(chunk: dict, terms: tuple[str, ...]) -> bool:
    if not terms:
        return True
    text = f"{chunk.get('title', '')} {chunk.get('text', '')}".lower()
    return any(term in text for term in terms)
