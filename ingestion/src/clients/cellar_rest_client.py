"""CELLAR REST API client for EUR-Lex document retrieval."""
import asyncio
import logging
import time

import httpx

logger = logging.getLogger(__name__)

CELLAR_BASE = "https://publications.europa.eu/resource/cellar"
ELI_BASE = "http://data.europa.eu/eli"
EURLEX_CONTENT = "https://eur-lex.europa.eu/legal-content"
RETRYABLE_STATUS = {429, 503, 502, 504}
DEFAULT_MAX_RETRIES = 3
DEFAULT_DELAY_SECONDS = 0.0


class CellarRestClient:
    """Fetches document content from CELLAR REST API."""

    def __init__(
        self,
        timeout: float = 60.0,
        delay_seconds: float = DEFAULT_DELAY_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._timeout = timeout
        self._delay_seconds = delay_seconds
        self._max_retries = max_retries
        self._last_request_at = 0.0

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
        await self._respect_rate_limit()
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self._timeout, follow_redirects=True
                ) as client:
                    response = await client.get(url, headers=headers)
                    if response.status_code in RETRYABLE_STATUS:
                        raise httpx.HTTPStatusError(
                            f"Retryable status {response.status_code}",
                            request=response.request,
                            response=response,
                        )
                    response.raise_for_status()
                    self._last_request_at = time.monotonic()
                    return response.content
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    break
                wait = min(2 ** attempt * self._delay_seconds or 1.0, 30.0)
                logger.warning("EUR-Lex fetch retry %s for %s in %.1fs", attempt + 1, url, wait)
                await asyncio.sleep(wait)
        assert last_error is not None
        raise last_error

    async def _respect_rate_limit(self) -> None:
        if self._delay_seconds <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._delay_seconds:
            await asyncio.sleep(self._delay_seconds - elapsed)
