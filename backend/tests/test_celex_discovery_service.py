"""Unit tests for CELEX discovery service."""
from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.utils.celex_title_normalize import (
    normalize_question_for_discovery,
    score_title_overlap,
    tokenize_meaningful,
)

ENV_QUESTION = (
    "Welke verplichtingen legt de Europese Milieuaansprakelijkheidsrichtlijn "
    "op aan exploitanten die milieuschade veroorzaken?"
)


def test_normalize_strips_richtlijn_suffix():
    normalized = normalize_question_for_discovery("milieuaansprakelijkheidsrichtlijn verplichtingen")
    assert "richtlijn" not in normalized.split()
    assert "milieuaansprakelijkheidsrichtlijn" in normalized or "milieuaansprakelijkheid" in normalized


def test_score_title_overlap_compound_term():
    tokens = tokenize_meaningful(ENV_QUESTION)
    score = score_title_overlap(tokens, "milieuaansprakelijkheid milieuschade")
    assert score >= 0.5


def test_discover_sync_finds_environmental_liability_celex():
    service = CelexDiscoveryService()
    hits = service.discover_sync(ENV_QUESTION, limit=3)
    celexes = [hit.celex for hit in hits]
    assert "32004L0035" in celexes
    top = hits[0]
    assert top.celex == "32004L0035"
    assert top.score >= 0.75


def test_high_confidence_celex_for_milieu_question():
    celex = CelexDiscoveryService().high_confidence_celex(ENV_QUESTION)
    assert celex == "32004L0035"
