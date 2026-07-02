"""FastAPI auth dependencies for JWT and RBAC."""
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from backend.src.config import settings
from backend.src.security.rbac_matrix import Permission, role_has_permission
from backend.src.services.auth_service import AuthService
from backend.src.services.rbac_service import RbacService

auth_service = AuthService()
rbac_service = RbacService()


@dataclass(slots=True)
class Principal:
    user_id: str | None
    email: str | None
    role: str


async def get_current_principal(
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> Principal:
    if x_admin_key and settings.admin_api_key.strip() and x_admin_key == settings.admin_api_key.strip():
        return Principal(user_id=None, email=None, role="admin")
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = auth_service.decode_token(token)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None
        return Principal(
            user_id=str(payload.get("sub")),
            email=payload.get("email"),
            role=str(payload.get("role", "user")),
        )
    if settings.jwt_auth_required:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return Principal(user_id=None, email=None, role="user")


def _is_admin_dev_open() -> bool:
    return not settings.admin_api_key.strip() and not settings.jwt_auth_required


def require_permission(permission: Permission):
    async def _guard(principal: Principal = Depends(get_current_principal)) -> Principal:
        if _is_admin_dev_open() and permission in {Permission.ADMIN_READ, Permission.ADMIN_WRITE}:
            return principal
        if not role_has_permission(principal.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": f"Missing permission: {permission.value}"},
            )
        return principal

    return _guard


async def require_admin_access(
    principal: Principal = Depends(get_current_principal),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> Principal:
    if principal.role == "admin":
        return principal
    rbac_service.require_admin(x_admin_key)
    return principal
