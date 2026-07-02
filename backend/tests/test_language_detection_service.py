"""Tests for language detection and resolution."""
from backend.src.services.language_detection_service import LanguageDetectionService
from backend.src.services.language_resolution_service import LanguageResolutionService


def test_detects_french_question() -> None:
    detector = LanguageDetectionService()
    assert detector.detect("Quelles obligations impose le RGPD?") == "fr"


def test_detects_german_question() -> None:
    detector = LanguageDetectionService()
    assert detector.detect("Welche Pflichten gelten nach der DSGVO?") == "de"


def test_detects_spanish_question() -> None:
    detector = LanguageDetectionService()
    assert detector.detect("¿Qué regula el RGPD según la directiva?") == "es"


def test_auto_resolution_uses_detection() -> None:
    resolver = LanguageResolutionService()
    assert resolver.resolve("auto", "Quelles obligations impose le RGPD?") == "fr"


def test_unknown_language_falls_back_to_nl() -> None:
    resolver = LanguageResolutionService()
    assert resolver.resolve("xx", "Test question") == "nl"
