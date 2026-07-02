"""Tests for SSRF guard helpers."""
import pytest

from backend.src.security.ssrf_guard import (
    SecurityValidationError,
    assert_url_allowed,
    validate_celex,
)


def test_validate_celex_accepts_standard_format():
    assert validate_celex("32022r2065") == "32022R2065"


def test_validate_celex_rejects_injection():
    with pytest.raises(SecurityValidationError):
        validate_celex("http://evil.test")


def test_assert_url_allowed_accepts_eurlex():
    assert_url_allowed("https://eur-lex.europa.eu/legal-content/nl/TXT/HTML/?uri=CELEX:32022R2065")


def test_assert_url_allowed_blocks_private_host():
    with pytest.raises(SecurityValidationError):
        assert_url_allowed("https://127.0.0.1/internal")
