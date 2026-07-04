"""Tests for EUR-Lex content usability heuristics."""
from backend.src.utils.legal_content_quality import is_usable_content_bytes


def test_eurlex_html_with_navigation_is_usable_when_legal_body_present():
    html = (
        b"<!DOCTYPE html><html><head><title>EUR-Lex</title></head><body>"
        b"<nav>Skip to main content | My EUR-Lex | Sign in</nav>"
        b"<div class='eli-subdivision'>Artikel 116 Terugbetaling en kwijtschelding. "
        b"De douaneautoriteiten betalen het bedrag terug wanneer het bedrag de "
        b"wettelijk verschuldigde douaneschuld overschrijdt.</div>"
        + b"x" * 500
        + b"</body></html>"
    )
    assert is_usable_content_bytes(html) is True


def test_bot_challenge_page_is_rejected():
    html = b"<html><body>Please wait while we verify you are not a robot</body></html>"
    assert is_usable_content_bytes(html) is False
