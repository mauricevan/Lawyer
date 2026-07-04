"""Rate-limit key helpers for audit CI runs."""
import secrets

from fastapi import Request

from backend.src.config import settings


def is_audit_request(request: Request) -> bool:
    token = request.headers.get("x-audit-token", "")
    expected = settings.audit_run_token
    if not token or not expected:
        return False
    return secrets.compare_digest(token, expected)


def audit_or_ip_key(request: Request) -> str:
    if is_audit_request(request):
        return "audit-runner"
    return request.client.host if request.client else "unknown"
