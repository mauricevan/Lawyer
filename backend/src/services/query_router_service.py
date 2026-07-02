"""Rule-based query routing for legal retrieval strategy selection."""
from dataclasses import dataclass, field
import re

from backend.src.services.language_resolution_service import LanguageResolutionService
from ingestion.src.data.domain_registry_loader import get_domain_keywords
from ingestion.src.data.legal_term_hints import match_primary_celex_hint

DOMAIN_KEYWORDS = get_domain_keywords()

DOC_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "regulation": ("verordening", "regulation"),
    "directive": ("richtlijn", "directive"),
    "decision": ("besluit", "decision"),
}

CURRENT_TIME_HINTS = ("huidig", "actueel", "nu", "in force", "geldig")
HISTORICAL_TIME_HINTS = ("historisch", "toen", "vroeger", "oud", "wijziging sinds")


@dataclass(slots=True)
class QueryRoute:
    """Structured route decision used by retrieval."""

    domains: list[str] = field(default_factory=list)
    doc_types: list[str] = field(default_factory=list)
    time_context: str = "current"
    keywords: list[str] = field(default_factory=list)
    celex_hint: str | None = None
    language: str = "nl"

    def as_dict(self) -> dict[str, object]:
        return {
            "domains": self.domains,
            "doc_types": self.doc_types,
            "time_context": self.time_context,
            "keywords": self.keywords,
            "celex_hint": self.celex_hint,
            "language": self.language,
        }


class QueryRouterService:
    """Determines legal retrieval strategy based on user intent."""

    def __init__(self) -> None:
        self._language = LanguageResolutionService()

    def route(self, question: str, preferred_language: str = "nl") -> QueryRoute:
        question_lower = question.lower()
        domains = self._match_categories(question_lower, DOMAIN_KEYWORDS)
        doc_types = self._match_categories(question_lower, DOC_TYPE_KEYWORDS)
        time_context = self._infer_time_context(question_lower)
        celex_hint = self._extract_celex(question)
        keywords = self._extract_keywords(question)
        language = self._language.resolve(preferred_language, question)
        return QueryRoute(
            domains=domains,
            doc_types=doc_types,
            time_context=time_context,
            keywords=keywords,
            celex_hint=celex_hint,
            language=language,
        )

    def _match_categories(
        self,
        text: str,
        categories: dict[str, tuple[str, ...]],
    ) -> list[str]:
        return [
            category
            for category, terms in categories.items()
            if any(term in text for term in terms)
        ]

    def _infer_time_context(self, text: str) -> str:
        if any(hint in text for hint in HISTORICAL_TIME_HINTS):
            return "historical"
        if any(hint in text for hint in CURRENT_TIME_HINTS):
            return "current"
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
