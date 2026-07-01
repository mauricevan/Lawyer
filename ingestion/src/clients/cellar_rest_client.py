"""CELLAR REST API client for EUR-Lex document retrieval."""
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CELLAR_BASE = "https://publications.europa.eu/resource/cellar"
ELI_BASE = "http://data.europa.eu/eli"
EURLEX_CONTENT = "https://eur-lex.europa.eu/legal-content"


class CellarRestClient:
    """Fetches document content from CELLAR REST API."""

    def __init__(self, timeout: float = 60.0) -> None:
        self._timeout = timeout

    async def fetch_by_celex(self, celex: str, language: str = "nl") -> bytes:
        """Fetch document HTML/XHTML via EUR-Lex content URL."""
        url = f"{EURLEX_CONTENT}/{language}/TXT/HTML/?uri=CELEX:{celex}"
        return await self._get(url, "text/html")

    async def fetch_xhtml(self, cellar_id: str, language: str = "nld") -> bytes:
        """Fetch XHTML manifestation from CELLAR."""
        url = f"{CELLAR_BASE}/{cellar_id}"
        headers = {"Accept": "application/xhtml+xml", "Accept-Language": language}
        return await self._get_with_headers(url, headers)

    async def fetch_formex(self, cellar_id: str) -> bytes:
        """Fetch Formex XML from CELLAR."""
        url = f"{CELLAR_BASE}/{cellar_id}"
        headers = {"Accept": "application/xml;type=fmx"}
        return await self._get_with_headers(url, headers)

    def build_eurlex_url(self, celex: str, language: str = "NL") -> str:
        return f"{EURLEX_CONTENT}/{language}/TXT/?uri=CELEX:{celex}"

    def build_eli_uri(self, doc_type: str, year: int, number: int) -> str:
        prefix = {"regulation": "reg", "directive": "dir", "decision": "dec"}.get(
            doc_type, "reg"
        )
        return f"{ELI_BASE}/{prefix}/{year}/{number}/oj"

    async def _get(self, url: str, accept: str) -> bytes:
        return await self._get_with_headers(url, {"Accept": accept})

    async def _get_with_headers(self, url: str, headers: dict[str, str]) -> bytes:
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
