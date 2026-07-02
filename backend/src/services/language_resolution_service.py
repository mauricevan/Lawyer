"""Resolve preferred, detected, and fallback languages for queries."""
from backend.src.services.language_detection_service import LanguageDetectionService
from ingestion.src.data.language_registry_loader import (
    get_enabled_languages,
    get_fetch_fallback_chain,
    is_language_enabled,
)

_AUTO_SENTINEL = "auto"
_DEFAULT = "nl"


class LanguageResolutionService:
    """Picks an enabled language and exposes EUR-Lex fallback chains."""

    def __init__(self) -> None:
        self._detector = LanguageDetectionService()

    def resolve(self, preferred: str | None, question: str) -> str:
        code = (preferred or _DEFAULT).lower().split("-")[0]
        if code == _AUTO_SENTINEL:
            code = self._detector.detect(question)
        if is_language_enabled(code):
            return code
        return _DEFAULT if is_language_enabled(_DEFAULT) else get_enabled_languages()[0]

    def fallback_chain(self, language: str) -> tuple[str, ...]:
        return get_fetch_fallback_chain(language)
