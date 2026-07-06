"""Load a full EUR-Lex act into an in-memory article session."""
import logging
from typing import Any

from backend.src.services.live_document_fetch_service import LiveDocumentFetchService
from backend.src.services.language_resolution_service import LanguageResolutionService
from ingestion.src.data.identity_sample_articles import (
    get_identity_sample_articles,
    is_offline_identity_celex,
)
from ingestion.src.data.treaty_sample_articles import (
    get_treaty_sample_articles,
    is_offline_treaty_celex,
)
from ingestion.src.parsers.document_parser import DocumentParser
from shared.schemas.eurlex_document import EurlexArticle, EurlexDocumentSession

logger = logging.getLogger(__name__)


class EurlexDocumentSessionService:
    """Fetch + parse one CELEX act into searchable articles."""

    def __init__(self) -> None:
        self._fetch = LiveDocumentFetchService()
        self._parser = DocumentParser()
        self._language = LanguageResolutionService()

    async def load(
        self,
        celex: str,
        language: str = "nl",
    ) -> EurlexDocumentSession | None:
        """Return parsed article map or None when live content is unusable."""
        if is_offline_treaty_celex(celex):
            offline = self._offline_curated_session(celex, language, get_treaty_sample_articles)
            if offline:
                return offline
        if is_offline_identity_celex(celex):
            offline = self._offline_curated_session(celex, language, get_identity_sample_articles)
            if offline:
                return offline
        for lang in self._language.fallback_chain(language):
            session = await self._try_load(celex, lang)
            if session and session.articles:
                return session
        if is_offline_identity_celex(celex):
            return self._offline_curated_session(celex, language, get_identity_sample_articles)
        if is_offline_treaty_celex(celex):
            return self._offline_curated_session(celex, language, get_treaty_sample_articles)
        return None

    def _offline_curated_session(
        self,
        celex: str,
        language: str,
        loader,
    ) -> EurlexDocumentSession | None:
        """Curated NL article text when live EUR-Lex fetch is unavailable."""
        subdivisions = loader(celex)
        if not subdivisions:
            return None
        articles = self._group_articles(subdivisions)
        if not articles:
            return None
        titles = {
            "32004L0038": "Richtlijn 2004/38/EG (verblijfsrecht EU-burgers)",
            "32014R0910": "Verordening (EU) nr. 910/2014 (eIDAS)",
            "12016E028": "Verdrag betreffende de werking van de Europese Unie (VWEU)",
        }
        return EurlexDocumentSession(
            celex=celex,
            title=titles.get(celex, f"EUR-Lex CELEX {celex}"),
            language=language,
            articles=articles,
            article_count=len(articles),
            fetch_source="offline_curated",
            is_consolidated=True,
        )

    async def _try_load(self, celex: str, language: str) -> EurlexDocumentSession | None:
        fetched = await self._fetch.fetch_document(celex, language)
        if not fetched:
            return None
        content, content_type, resolved_lang, title = fetched
        subdivisions = self._parser.parse(content, celex, content_type)
        if not subdivisions:
            logger.warning("eurlex_session_empty celex=%s lang=%s", celex, resolved_lang)
            return None
        articles = self._group_articles(subdivisions)
        return EurlexDocumentSession(
            celex=celex,
            title=title or f"EUR-Lex CELEX {celex}",
            language=resolved_lang,
            articles=articles,
            article_count=len(articles),
        )

    def _group_articles(self, subdivisions: list[dict[str, Any]]) -> dict[str, EurlexArticle]:
        grouped: dict[str, list[str]] = {}
        titles: dict[str, str] = {}
        types: dict[str, str] = {}
        for sub in subdivisions:
            number = self._article_key(sub.get("article_number"))
            if not number:
                continue
            text = str(sub.get("text", "")).strip()
            if not text:
                continue
            grouped.setdefault(number, []).append(text)
            if sub.get("title"):
                titles.setdefault(number, str(sub["title"]))
            types.setdefault(number, str(sub.get("subdivision_type", "article")))
        articles: dict[str, EurlexArticle] = {}
        for number, parts in grouped.items():
            articles[number] = EurlexArticle(
                article_number=number,
                title=titles.get(number, ""),
                text="\n\n".join(parts),
                subdivision_type=types.get(number, "article"),
            )
        return articles

    @staticmethod
    def _article_key(raw: Any) -> str | None:
        if raw is None:
            return None
        text = str(raw).strip()
        if not text:
            return None
        return text.lstrip("0") or "0"
