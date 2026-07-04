"""Tests for CellarRest-backed live document fetch."""
from unittest.mock import AsyncMock

import pytest

from backend.src.services.live_document_fetch_service import LiveDocumentFetchService

NAV_HTML = (
    b"<html><body>Skip to main content. My EUR-Lex sign in register. "
    b"Please wait while we load the page.</body></html>"
)
LEGAL_HTML = (
    b"<html><body><h2>Hoofdstuk 1</h2><p>"
    + (b"Levende paarden en ezels onder goederencode 0101 voor douane. " * 80)
    + b"0101 21 00 Fokdieren van zuiver ras.</p></body></html>"
)


@pytest.mark.asyncio
async def test_rejects_navigation_html():
    client = AsyncMock()
    client.fetch_by_celex = AsyncMock(return_value=NAV_HTML)
    service = LiveDocumentFetchService(client=client)
    result = await service.fetch_document("31987R2658", "nl")
    assert result is None


@pytest.mark.asyncio
async def test_accepts_usable_legal_html():
    client = AsyncMock()
    client.fetch_by_celex = AsyncMock(return_value=LEGAL_HTML)
    service = LiveDocumentFetchService(client=client)
    result = await service.fetch_document("31987R2658", "nl")
    assert result is not None
    content, content_type, language, title = result
    assert content == LEGAL_HTML
    assert content_type in {"html", "xml"}
    assert language == "nl"
