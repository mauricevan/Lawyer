"""Tests for admin RBAC guard."""
import pytest
from fastapi import HTTPException

from backend.src.config import settings
from backend.src.services.rbac_service import RbacService


def test_admin_open_when_key_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "")
    RbacService().require_admin(None)


def test_admin_rejects_missing_key(monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "secret")
    with pytest.raises(HTTPException) as exc:
        RbacService().require_admin(None)
    assert exc.value.status_code == 403


def test_admin_accepts_valid_key(monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "secret")
    RbacService().require_admin("secret")
