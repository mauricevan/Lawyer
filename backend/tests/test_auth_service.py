"""Tests for JWT auth service."""
from backend.src.services.auth_service import AuthService


def test_password_hash_and_verify_roundtrip():
    service = AuthService()
    hashed = service.hash_password("strong-password")
    assert service.verify_password("strong-password", hashed)
    assert not service.verify_password("wrong-password", hashed)


def test_create_and_decode_access_token():
    service = AuthService()
    token = service.create_access_token("user-1", "dev@example.com", "admin")
    payload = service.decode_token(token)
    assert payload["sub"] == "user-1"
    assert payload["role"] == "admin"
