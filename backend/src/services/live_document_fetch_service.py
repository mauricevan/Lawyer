"""Fetch EUR-Lex documents via CellarRest with usable-content validation."""
import logging
import re

from backend.src.config import settings
from ingestion.src.clients.cellar_rest_client import CellarRestClient

from backend.src.utils.legal_content_quality import is_usable_content_bytes

logger = logging.getLogger(__name__)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class LiveDocumentFetchService:
    """Loads live documents using the same path as curated ingest."""

    def __init__(self, client: CellarRestClient | None = None) -> None:
        timeout = max(settings.live_fallback_timeout_seconds, 25.0)
        self._client = client or CellarRestClient(timeout=timeout)

    async def fetch_document(
        self,
        celex: str,
        language: str = "nl",
    ) -> tuple[bytes, str, str, str] | None:
        """Return (content, content_type, resolved_language, title) or None."""
        try:
            content = await self._client.fetch_by_celex(celex, language)
        except Exception as exc:
            logger.warning("live_fetch_usable=false celex=%s reason=fetch_failed detail=%s", celex, exc)
            return None
        if not is_usable_content_bytes(content):
            logger.warning("live_fetch_usable=false celex=%s reason=navigation_or_short", celex)
            return None
        content_type = "xml" if content.lstrip()[:1] == b"<" and b"html" not in content[:200].lower() else "html"
        title = self._extract_title(content)
        return content, content_type, language, title

    @staticmethod
    def _extract_title(content: bytes) -> str:
        text = content.decode("utf-8", errors="ignore")
        match = TITLE_RE.search(text)
        return match.group(1).strip() if match else ""
