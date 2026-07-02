"""Security regression tests for RBAC matrix and auth dependencies."""
import pytest
from fastapi import HTTPException

from backend.src.config import settings
from backend.src.dependencies.auth import Principal, get_current_principal, require_permission
from backend.src.security.rbac_matrix import Permission, role_has_permission
from backend.src.services.auth_service import AuthService


def test_role_matrix_grants_user_query_permission():
    assert role_has_permission("user", Permission.QUERY)


def test_role_matrix_denies_user_admin_write():
    assert not role_has_permission("user", Permission.ADMIN_WRITE)


@pytest.mark.asyncio
async def test_get_current_principal_allows_anonymous_in_dev(monkeypatch):
    monkeypatch.setattr(settings, "jwt_auth_required", False)
    principal = await get_current_principal(authorization=None, x_admin_key=None)
    assert principal.role == "user"


@pytest.mark.asyncio
async def test_get_current_principal_requires_auth_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "jwt_auth_required", True)
    with pytest.raises(HTTPException) as exc:
        await get_current_principal(authorization=None, x_admin_key=None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_principal_accepts_bearer_token(monkeypatch):
    monkeypatch.setattr(settings, "jwt_auth_required", True)
    token = AuthService().create_access_token("uid", "a@b.nl", "analyst")
    principal = await get_current_principal(authorization=f"Bearer {token}", x_admin_key=None)
    assert principal.role == "analyst"


@pytest.mark.asyncio
async def test_require_permission_blocks_analyst_admin_write(monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "configured")
    monkeypatch.setattr(settings, "jwt_auth_required", True)
    guard = require_permission(Permission.ADMIN_WRITE)
    with pytest.raises(HTTPException) as exc:
        await guard(Principal(user_id="1", email="a@b.nl", role="analyst"))
    assert exc.value.status_code == 403
