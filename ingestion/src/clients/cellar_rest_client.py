"""CELLAR REST API client for EUR-Lex document retrieval."""
import asyncio
import logging
import time

import httpx

from backend.src.security.ssrf_guard import assert_url_allowed, validate_celex
from ingestion.src.clients.eurlex_fetch_urls import build_fetch_urls

logger = logging.getLogger(__name__)

CELLAR_BASE = "https://publications.europa.eu/resource/cellar"
ELI_BASE = "http://data.europa.eu/eli"
RETRYABLE_STATUS = {429, 502, 503, 504}
PENDING_STATUS = {202}
DEFAULT_MAX_RETRIES = 3
DEFAULT_DELAY_SECONDS = 0.0
DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; LawyerRAG/1.0; +https://localhost)"
MIN_CONTENT_BYTES = 4000
PENDING_POLL_ATTEMPTS = 6
PENDING_POLL_SECONDS = 2.0


class CellarRestClient:
    """Fetches document content from EUR-Lex with retries and format fallbacks."""

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
        """Fetch document content via ordered EUR-Lex URL candidates."""
        safe_celex = validate_celex(celex)
        errors: list[str] = []
        for url, content_type in build_fetch_urls(safe_celex, language):
            assert_url_allowed(url)
            try:
                content = await self._fetch_url(url)
                if self._is_usable_content(content):
                    return content
                errors.append(f"{content_type}:{len(content)}B")
            except Exception as exc:
                errors.append(f"{content_type}:{exc}")
        joined = "; ".join(errors[:4])
        raise httpx.HTTPError(f"No usable EUR-Lex content for {safe_celex} ({joined})")

    async def fetch_xhtml(self, cellar_id: str, language: str = "nld") -> bytes:
        url = f"{CELLAR_BASE}/{cellar_id}"
        assert_url_allowed(url)
        headers = {"Accept": "application/xhtml+xml", "Accept-Language": language}
        return await self._fetch_url(url, headers=headers)

    async def fetch_formex(self, cellar_id: str) -> bytes:
        url = f"{CELLAR_BASE}/{cellar_id}"
        assert_url_allowed(url)
        headers = {"Accept": "application/xml;type=fmx"}
        return await self._fetch_url(url, headers=headers)

    def build_eurlex_url(self, celex: str, language: str = "NL") -> str:
        return build_fetch_urls(celex, language.lower())[0][0]

    def build_eli_uri(self, doc_type: str, year: int, number: int) -> str:
        prefix = {"regulation": "reg", "directive": "dir", "decision": "dec"}.get(doc_type, "reg")
        return f"{ELI_BASE}/{prefix}/{year}/{number}/oj"

    async def _fetch_url(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        request_headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        if headers:
            request_headers.update(headers)
        await self._respect_rate_limit()
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                content = await self._get_once(url, request_headers)
                if content:
                    self._last_request_at = time.monotonic()
                    return content
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    break
                wait = min(2 ** attempt * (self._delay_seconds or 1.0), 30.0)
                logger.warning("EUR-Lex fetch retry %s for %s in %.1fs", attempt + 1, url, wait)
                await asyncio.sleep(wait)
        assert last_error is not None
        raise last_error

    async def _get_once(self, url: str, headers: dict[str, str]) -> bytes:
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await self._get_response(client, url, headers)
            if response.status_code in PENDING_STATUS:
                if self._is_usable_content(response.content):
                    return response.content
                for poll in range(1, PENDING_POLL_ATTEMPTS):
                    if not response.content:
                        break
                    await asyncio.sleep(PENDING_POLL_SECONDS)
                    response = await self._get_response(client, url, headers)
                    if self._is_usable_content(response.content):
                        return response.content
                return b""
            response.raise_for_status()
            return response.content

    async def _get_response(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: dict[str, str],
    ) -> httpx.Response:
        response = await client.get(url, headers=headers)
        if response.status_code in RETRYABLE_STATUS:
            raise httpx.HTTPStatusError(
                f"Retryable status {response.status_code}",
                request=response.request,
                response=response,
            )
        return response

    def _is_usable_content(self, content: bytes) -> bool:
        if len(content) < MIN_CONTENT_BYTES:
            return False
        lowered = content[:2000].lower()
        if b"please wait" in lowered or b"just a moment" in lowered:
            return False
        return b"<" in content[:500]

    async def _respect_rate_limit(self) -> None:
        if self._delay_seconds <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._delay_seconds:
            await asyncio.sleep(self._delay_seconds - elapsed)
