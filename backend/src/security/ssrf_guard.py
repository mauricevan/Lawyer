"""SSRF and outbound URL safety checks for live EUR-Lex fetches."""
import ipaddress
import re
from urllib.parse import urlparse

CELEX_PATTERN = re.compile(r"^\d{5}[A-Z]\d{3,4}([A-Z()0-9]+)?$")
ALLOWED_HOSTS = frozenset({
    "eur-lex.europa.eu",
    "publications.europa.eu",
})


class SecurityValidationError(ValueError):
    """Raised when outbound fetch parameters fail security validation."""


def validate_celex(celex: str) -> str:
    """Normalize and validate CELEX before building outbound URLs."""
    cleaned = celex.strip().upper()
    if not CELEX_PATTERN.match(cleaned):
        raise SecurityValidationError("Invalid CELEX identifier")
    return cleaned


def assert_url_allowed(url: str) -> None:
    """Reject URLs outside the approved EUR-Lex/CELLAR host allowlist."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise SecurityValidationError("Only HTTPS URLs are allowed")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise SecurityValidationError("Outbound host is not allowed")
    if host and _is_private_host(host):
        raise SecurityValidationError("Private network targets are blocked")


def _is_private_host(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return host in {"localhost", "127.0.0.1", "0.0.0.0"}
    return ip.is_private or ip.is_loopback or ip.is_link_local
