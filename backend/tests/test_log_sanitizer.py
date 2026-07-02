"""Tests for log message sanitization."""
from backend.src.utils.log_sanitizer import sanitize_log_message


def test_redacts_openrouter_key() -> None:
    raw = "failed with sk-or-v1-abc123secretkey"
    assert "abc123" not in sanitize_log_message(raw)
    assert "[REDACTED]" in sanitize_log_message(raw)


def test_redacts_bearer_token() -> None:
    raw = "auth failed Bearer eyJhbGciOiJIUzI1NiJ9.payload"
    assert "eyJhbGci" not in sanitize_log_message(raw)


def test_preserves_safe_message() -> None:
    msg = "query completed in 120ms"
    assert sanitize_log_message(msg) == msg
