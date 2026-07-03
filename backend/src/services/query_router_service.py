"""Rule-based query routing for legal retrieval strategy selection."""
import re

from backend.src.models.query_route import QueryRoute
from backend.src.services.domain_cluster_service import DomainClusterService
from backend.src.services.language_resolution_service import LanguageResolutionService
from backend.src.utils.intent_library_loader import QueryIntent, load_intent_library, match_intent
from ingestion.src.data.domain_registry_loader import get_domain_keywords
from ingestion.src.data.legal_term_hints import match_primary_celex_hint

DOMAIN_KEYWORDS = get_domain_keywords()

DOC_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "regulation": ("verordening", "regulation"),
    "directive": ("richtlijn", "directive"),
    "decision": ("besluit", "decision"),
}

HISTORICAL_TIME_HINTS = ("historisch", "toen", "vroeger", "oud", "wijziging sinds")


class QueryRouterService:
    """Determines legal retrieval strategy based on user intent."""

    def __init__(self) -> None:
        self._language = LanguageResolutionService()
        self._cluster = DomainClusterService()
        _, self._low_confidence_threshold = load_intent_library()

    def route(self, question: str, preferred_language: str = "nl") -> QueryRoute:
        intent = match_intent(question)
        if intent is not None:
            route = self._route_from_intent(question, preferred_language, intent)
        else:
            route = self._route_from_keywords(question, preferred_language)
        return self._cluster.enrich(question, route, self._low_confidence_threshold)

    def _route_from_intent(self, question: str, preferred_language: str, intent: QueryIntent) -> QueryRoute:
        domains = [intent.domain] if intent.domain else []
        doc_types = [intent.doc_type] if intent.doc_type else []
        time_context = intent.time_context or self._infer_time_context(question.lower())
        return QueryRoute(
            domains=domains,
            doc_types=doc_types,
            time_context=time_context,
            keywords=self._extract_keywords(question),
            celex_hint=intent.celex_hint or self._extract_celex(question),
            language=self._language.resolve(preferred_language, question),
            intent_id=intent.intent_id,
            confidence=intent.confidence,
        )

    def _route_from_keywords(self, question: str, preferred_language: str) -> QueryRoute:
        question_lower = question.lower()
        domains = self._match_categories(question_lower, DOMAIN_KEYWORDS)
        doc_types = self._match_categories(question_lower, DOC_TYPE_KEYWORDS)
        confidence = 0.75 if len(domains) == 1 else 0.55 if domains else 0.4
        return QueryRoute(
            domains=domains,
            doc_types=doc_types,
            time_context=self._infer_time_context(question_lower),
            keywords=self._extract_keywords(question),
            celex_hint=self._extract_celex(question),
            language=self._language.resolve(preferred_language, question),
            confidence=confidence,
        )

    def _match_categories(self, text: str, categories: dict[str, tuple[str, ...]]) -> list[str]:
        return [name for name, terms in categories.items() if any(term in text for term in terms)]

    def _infer_time_context(self, text: str) -> str:
        if any(hint in text for hint in HISTORICAL_TIME_HINTS):
            return "historical"
        return "current"

    def _extract_celex(self, question: str) -> str | None:
        return match_primary_celex_hint(question)

    def _extract_keywords(self, question: str) -> list[str]:
        words = re.findall(r"[A-Za-zÀ-ÿ0-9-]{4,}", question.lower())
        seen: set[str] = set()
        keywords: list[str] = []
        for word in words:
            if word not in seen:
                seen.add(word)
                keywords.append(word)
            if len(keywords) == 8:
                break
        return keywords
