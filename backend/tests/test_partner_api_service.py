"""Tests for partner API service (plan31 AA)."""
import os

from backend.src.services.partner_api_service import PartnerApiService


def test_partner_api_audit_passes():
    assert PartnerApiService().audit()["passed"]


def test_partner_resolution_with_env_key(monkeypatch):
    monkeypatch.setenv("PARTNER_PILOT_API_KEY", "test-partner-secret")
    partner = PartnerApiService().resolve_partner("test-partner-secret")
    assert partner is not None
    assert partner.partner_id == "pilot-partner"


def test_partner_rejects_invalid_key(monkeypatch):
    monkeypatch.setenv("PARTNER_PILOT_API_KEY", "valid")
    assert PartnerApiService().resolve_partner("invalid") is None
