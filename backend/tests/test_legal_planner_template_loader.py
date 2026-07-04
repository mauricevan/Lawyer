"""Tests for centralized obligation template loader."""
from backend.src.services.legal_planner_template_loader import resolve_obligation_templates


def test_resolve_by_plan_id():
    templates = resolve_obligation_templates("flight_compensation", "32004R0261", "transport")
    assert len(templates) >= 3
    assert templates[0]["label"]


def test_resolve_by_domain_id():
    templates = resolve_obligation_templates("gdpr", "32016R0679", "privacy")
    assert len(templates) >= 3


def test_resolve_by_celex_for_discovery():
    templates = resolve_obligation_templates("discovery", "32000L0078", None)
    assert len(templates) >= 3
    assert any("discriminatie" in t["uitleg"].lower() for t in templates)


def test_resolve_by_legal_domain_fallback():
    templates = resolve_obligation_templates("unknown_plan", "999999X9999", "customs")
    assert len(templates) >= 3
