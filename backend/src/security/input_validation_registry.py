"""Registry of API endpoints and their input validation coverage."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointValidation:
    method: str
    path: str
    body_schema: str | None
    path_validation: str | None
    query_validation: str | None
    auth_guard: str
    status: str


ENDPOINT_VALIDATIONS: tuple[EndpointValidation, ...] = (
    EndpointValidation("POST", "/api/v1/query", "QueryRequest", None, None, "QUERY", "validated"),
    EndpointValidation("POST", "/api/v1/query/stream", "QueryRequest", None, None, "QUERY", "validated"),
    EndpointValidation("POST", "/api/v1/auth/token", "TokenRequest", None, None, "public", "validated"),
    EndpointValidation("POST", "/api/v1/auth/register", "RegisterRequest", None, None, "dev-only", "validated"),
    EndpointValidation("POST", "/api/v1/conversations", "CreateConversationRequest", None, None, "CONVERSATIONS", "validated"),
    EndpointValidation("GET", "/api/v1/conversations/{id}", None, "UUID", None, "CONVERSATIONS", "validated"),
    EndpointValidation("POST", "/api/v1/conversations/{id}/save", None, "UUID", "title<=200", "CONVERSATIONS", "validated"),
    EndpointValidation("GET", "/api/v1/export/pdf/{id}", None, "UUID", None, "EXPORT", "validated"),
    EndpointValidation("GET", "/api/v1/documents/{celex}", None, "CELEX", "limit/offset", "public", "validated"),
    EndpointValidation("POST", "/api/v1/feedback", "FeedbackRequest", None, None, "FEEDBACK", "validated"),
    EndpointValidation("GET", "/api/v1/admin/audit/logs", None, None, "limit/offset", "ADMIN_READ", "validated"),
    EndpointValidation("GET", "/api/v1/admin/ingestion-jobs", None, None, "limit<=200", "ADMIN_READ", "validated"),
    EndpointValidation("POST", "/api/v1/admin/retention/purge", None, None, None, "ADMIN_WRITE", "validated"),
)
