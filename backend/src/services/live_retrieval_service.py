"""Live fallback retrieval via CELLAR SPARQL and EUR-Lex content."""
import asyncio
import logging
import re
from collections.abc import Callable
from typing import Any

import httpx

from backend.src.config import settings
from backend.src.security.ssrf_guard import SecurityValidationError, assert_url_allowed, validate_celex
from backend.src.services.live_chunk_builder import LiveChunkBuilder
from backend.src.services.language_resolution_service import LanguageResolutionService
from ingestion.src.clients.sparql_client import SparqlClient

logger = logging.getLogger(__name__)
EURLEX_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
MAX_RETRIES = 3
CelexAllowedFn = Callable[[str, str | None], bool]


class LiveRetrievalService:
    """Fetches live legal context when local retrieval is insufficient."""

    def __init__(self) -> None:
        self._sparql = SparqlClient(timeout=settings.live_fallback_timeout_seconds)
        self._chunk_builder = LiveChunkBuilder()
        self._language = LanguageResolutionService()

    async def fallback_chunks(
        self,
        question: str,
        language: str = "nl",
        celex_hint: str | None = None,
        is_celex_allowed: CelexAllowedFn | None = None,
    ) -> list[dict[str, Any]]:
        if not settings.enable_live_fallback:
            return []
        celex = await self._resolve_celex(question, language, celex_hint, is_celex_allowed)
        if not celex:
            return []
        try:
            celex = validate_celex(celex)
        except SecurityValidationError:
            return []
        for lang in self._language.fallback_chain(language):
            metadata = await self._fetch_sparql_metadata(celex, lang)
            title, html = await self._fetch_document_html(celex, lang)
            if metadata and metadata.get("title"):
                title = metadata["title"]
            if not html:
                continue
            parsed = self._chunk_builder.build_from_html(celex, html, lang, title, metadata)
            if parsed:
                return parsed
            return self._build_chunks_from_plain_text(
                celex, title, html.decode("utf-8", errors="ignore"), lang, metadata,
            )
        return []

    async def _resolve_celex(
        self,
        question: str,
        language: str,
        celex_hint: str | None,
        is_celex_allowed: CelexAllowedFn | None,
    ) -> str | None:
        if celex_hint:
            return celex_hint if self._is_celex_allowed(celex_hint, language, is_celex_allowed) else None
        extracted = self._extract_celex(question)
        if extracted and self._is_celex_allowed(extracted, language, is_celex_allowed):
            return extracted
        return await self._discover_with_fallback(question, language, is_celex_allowed)

    def _is_celex_allowed(
        self,
        celex: str,
        language: str | None,
        is_celex_allowed: CelexAllowedFn | None,
    ) -> bool:
        if is_celex_allowed is None:
            return True
        return is_celex_allowed(celex, language)

    def _extract_celex(self, question: str) -> str | None:
        match = re.search(r"\b\d{5}[A-Z]\d{4}\b", question.upper())
        return match.group(0) if match else None

    async def _discover_with_fallback(
        self,
        question: str,
        language: str,
        is_celex_allowed: CelexAllowedFn | None = None,
    ) -> str | None:
        for lang in self._language.fallback_chain(language):
            celex = await self._discover_celex(question, lang)
            if celex and self._is_celex_allowed(celex, lang, is_celex_allowed):
                return celex
        return None

    async def _discover_celex(self, question: str, language: str) -> str | None:
        try:
            return await self._sparql.discover_celex_by_keywords(question, language)
        except Exception as exc:
            logger.warning("SPARQL discovery failed: %s", exc)
            return None

    async def _fetch_sparql_metadata(self, celex: str, language: str) -> dict[str, str] | None:
        try:
            return await self._sparql.fetch_work_by_celex(celex, language)
        except Exception as exc:
            logger.warning("SPARQL metadata lookup failed for %s: %s", celex, exc)
            return None

    async def _fetch_document_html(self, celex: str, language: str) -> tuple[str, bytes]:
        url = self._eurlex_url(celex, language)
        assert_url_allowed(url)
        timeout = settings.live_fallback_timeout_seconds
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url)
                    if response.status_code in (429, 503):
                        await asyncio.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                html = response.content
                title_match = EURLEX_TITLE_RE.search(response.text)
                title = title_match.group(1).strip() if title_match else ""
                return title, html
            except Exception as exc:
                logger.warning("Live fallback fetch failed (attempt %s): %s", attempt + 1, exc)
                await asyncio.sleep(2 ** attempt)
        return "", b""

    def _eurlex_url(self, celex: str, language: str) -> str:
        lang = (language or "NL").upper()
        return f"https://eur-lex.europa.eu/legal-content/{lang}/TXT/?uri=CELEX:{celex}"

    def _build_chunks_from_plain_text(
        self,
        celex: str,
        title: str,
        html_text: str,
        language: str,
        metadata: dict[str, str] | None,
    ) -> list[dict[str, Any]]:
        snippet = re.sub(r"<[^>]+>", " ", html_text)
        snippet = re.sub(r"\s+", " ", snippet).strip()[:2400]
        segments = [part.strip() for part in re.split(r"(?<=[.!?])\s+", snippet) if len(part.strip()) > 80]
        if not segments:
            segments = [snippet[:1200]]
        chunks: list[dict[str, Any]] = []
        for index, segment in enumerate(segments[:3], start=1):
            chunks.append({
                "chunk_id": f"live:{celex}:{index}",
                "celex": celex,
                "title": title or f"EUR-Lex CELEX {celex}",
                "text": segment,
                "article_number": str(index),
                "language": language,
                "is_consolidated": False,
                "is_in_force": True,
                "eli_uri": metadata.get("modified") if metadata else None,
                "score": 1.0,
                "source": "live_fallback",
            })
        return chunks
