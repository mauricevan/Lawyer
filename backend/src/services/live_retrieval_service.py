"""Live fallback retrieval via CELLAR REST and EUR-Lex content."""
import logging
import re
from collections.abc import Callable
from typing import Any

from backend.src.config import settings
from backend.src.security.ssrf_guard import SecurityValidationError, validate_celex
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.live_chunk_builder import LiveChunkBuilder
from backend.src.services.live_document_fetch_service import LiveDocumentFetchService
from backend.src.services.language_resolution_service import LanguageResolutionService
from backend.src.utils.article_resolver import resolve_article_number
from backend.src.utils.legal_content_quality import is_usable_legal_text, strip_html_tags
from ingestion.src.clients.sparql_client import SparqlClient

logger = logging.getLogger(__name__)
CelexAllowedFn = Callable[[str, str | None], bool]


class LiveRetrievalService:
    """Fetches live legal context when local retrieval is insufficient."""

    def __init__(self) -> None:
        self._sparql = SparqlClient(timeout=settings.live_fallback_timeout_seconds)
        self._chunk_builder = LiveChunkBuilder()
        self._document_fetch = LiveDocumentFetchService()
        self._quality = ChunkQualityService()
        self._language = LanguageResolutionService()
        self._planner = LegalSourcePlannerService()

    async def fallback_chunks(
        self,
        question: str,
        language: str = "nl",
        celex_hint: str | None = None,
        is_celex_allowed: CelexAllowedFn | None = None,
        article_hints: tuple[str, ...] | None = None,
        strict_articles: bool = False,
        search_keywords: tuple[str, ...] | None = None,
        agent_mode: bool = False,
    ) -> list[dict[str, Any]]:
        if not settings.enable_live_fallback:
            return []
        celex = await self._resolve_celex(question, language, celex_hint, is_celex_allowed)
        if not celex:
            return []
        source_plan = self._planner.plan(question)
        if source_plan and not celex_hint:
            celex = source_plan.celex
        if not article_hints and source_plan:
            article_hints = source_plan.articles
        try:
            celex = validate_celex(celex)
        except SecurityValidationError:
            return []
        fetch_languages = (language,) if agent_mode else self._language.fallback_chain(language)
        for lang in fetch_languages:
            metadata = await self._fetch_sparql_metadata(celex, lang)
            fetched = await self._document_fetch.fetch_document(celex, lang)
            if not fetched:
                continue
            content, _content_type, resolved_lang, title = fetched
            if metadata and metadata.get("title"):
                title = metadata["title"]
            parsed = self._chunk_builder.build_from_html(
                celex,
                content,
                resolved_lang,
                title,
                metadata,
                question=question,
                article_hints=article_hints,
                strict_articles=strict_articles,
                search_keywords=search_keywords,
                agent_mode=agent_mode,
            )
            parsed = self._quality.filter_chunks(parsed, expected_language=language)
            if parsed:
                return parsed
            plain = self._build_chunks_from_plain_text(
                celex, title, content.decode("utf-8", errors="ignore"), resolved_lang, metadata,
            )
            plain = self._quality.filter_chunks(plain, expected_language=language)
            if plain:
                return plain
            if resolved_lang != language:
                continue
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
            candidates = await self._sparql.discover_celex_candidates(question, language, limit=3)
            if candidates:
                return candidates[0].get("celex") or None
            return None
        except Exception as exc:
            logger.warning("SPARQL discovery failed: %s", exc)
            return None

    async def _fetch_sparql_metadata(self, celex: str, language: str) -> dict[str, str] | None:
        try:
            return await self._sparql.fetch_work_by_celex(celex, language)
        except Exception as exc:
            logger.warning("SPARQL metadata lookup failed for %s: %s", celex, exc)
            return None

    def _build_chunks_from_plain_text(
        self,
        celex: str,
        title: str,
        html_text: str,
        language: str,
        metadata: dict[str, str] | None,
    ) -> list[dict[str, Any]]:
        snippet = strip_html_tags(html_text)
        if not is_usable_legal_text(snippet):
            return []
        segments = [part.strip() for part in re.split(r"(?<=[.!?])\s+", snippet) if len(part.strip()) > 80]
        if not segments:
            segments = [snippet[:1200]]
        chunks: list[dict[str, Any]] = []
        for index, segment in enumerate(segments[:3], start=1):
            chunk = {
                "chunk_id": f"live:{celex}:{index}",
                "celex": celex,
                "title": title or f"EUR-Lex CELEX {celex}",
                "text": segment,
                "language": language,
                "is_consolidated": False,
                "is_in_force": True,
                "eli_uri": metadata.get("modified") if metadata else None,
                "score": 1.0,
                "source": "live_fallback",
            }
            chunk["article_number"] = resolve_article_number(chunk) or str(index)
            chunks.append(chunk)
        return chunks
