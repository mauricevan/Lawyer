"""Role-based access checks for admin and sensitive endpoints."""
from fastapi import Header, HTTPException, status

from backend.src.config import settings


class RbacService:
    """Validates admin access via optional API key."""

    def require_admin(self, admin_key: str | None) -> None:
        expected = settings.admin_api_key.strip()
        if not expected:
            return
        if not admin_key or admin_key != expected:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Admin access required."},
            )


rbac_service = RbacService()


def admin_auth(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")) -> None:
    rbac_service.require_admin(x_admin_key)
