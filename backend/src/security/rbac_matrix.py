"""Endpoint-level RBAC permission matrix."""
from enum import Enum


class Permission(str, Enum):
    QUERY = "query"
    CONVERSATIONS = "conversations"
    EXPORT = "export"
    FEEDBACK = "feedback"
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "anonymous": frozenset({Permission.QUERY, Permission.CONVERSATIONS, Permission.EXPORT, Permission.FEEDBACK}),
    "user": frozenset({Permission.QUERY, Permission.CONVERSATIONS, Permission.EXPORT, Permission.FEEDBACK}),
    "analyst": frozenset({
        Permission.QUERY,
        Permission.CONVERSATIONS,
        Permission.EXPORT,
        Permission.FEEDBACK,
        Permission.ADMIN_READ,
    }),
    "admin": frozenset(Permission),
}


def role_has_permission(role: str, permission: Permission) -> bool:
    """Return True when the role may perform the permission."""
    if role == "admin":
        return True
    allowed = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["anonymous"])
    return permission in allowed
