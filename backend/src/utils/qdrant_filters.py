"""Build Qdrant filters from query filter schema."""
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

from shared.schemas.query import QueryFilters

DOC_TYPE_CELEX_LETTER = {
    "regulation": "R",
    "directive": "L",
    "decision": "D",
}


def build_qdrant_filter(
    filters: QueryFilters | None,
    language: str | None,
    in_force_only: bool,
    excluded_celex: set[str] | None = None,
) -> Filter | None:
    """Translate API filters into a Qdrant filter object."""
    must_conditions: list[FieldCondition] = []
    must_not_conditions: list[FieldCondition] = []
    lang = filters.language if filters and filters.language else language
    if lang:
        must_conditions.append(
            FieldCondition(key="language", match=MatchValue(value=lang))
        )
    force_only = in_force_only
    if filters and filters.time_context == "historical":
        force_only = False
    if force_only:
        must_conditions.append(
            FieldCondition(key="is_in_force", match=MatchValue(value=True))
        )
    if filters and filters.celex:
        must_conditions.append(
            FieldCondition(key="celex", match=MatchValue(value=filters.celex))
        )
    if excluded_celex:
        must_not_conditions.append(
            FieldCondition(key="celex", match=MatchAny(any=sorted(excluded_celex)))
        )
    if not must_conditions and not must_not_conditions:
        return None
    return Filter(must=must_conditions, must_not=must_not_conditions)


def doc_type_matches_celex(doc_type: str, celex: str) -> bool:
    """Match CELEX type letter against requested document type."""
    expected = DOC_TYPE_CELEX_LETTER.get(doc_type)
    if not expected or len(celex) < 6:
        return True
    return celex[5].upper() == expected
