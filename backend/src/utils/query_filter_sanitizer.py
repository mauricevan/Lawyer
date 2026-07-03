"""Sanitize query filters based on caller authorization."""
from backend.src.security.rbac_matrix import Permission, role_has_permission
from shared.schemas.query import QueryFilters, QueryRequest


def sanitize_query_request(request: QueryRequest, role: str) -> QueryRequest:
    """Strip privileged filter flags when the caller lacks admin read access."""
    if not request.filters or not request.filters.include_deprecated:
        return request
    if role_has_permission(role, Permission.ADMIN_READ):
        return request
    return request.model_copy(
        update={"filters": request.filters.model_copy(update={"include_deprecated": False})},
    )


def privileged_filter_flags(filters: QueryFilters | None) -> tuple[str, bool]:
    """Return cache-relevant privileged filter fields."""
    if not filters:
        return "", False
    return filters.celex or "", filters.include_deprecated
