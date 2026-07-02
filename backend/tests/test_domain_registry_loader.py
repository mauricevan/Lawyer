"""Tests for domain registry loader."""
from ingestion.src.data.domain_registry_loader import (
    get_domain_keywords,
    load_domain_registry,
    resolve_domain_for_celex,
)


def test_registry_loads_go_domains() -> None:
    registry = load_domain_registry()
    assert "privacy" in registry
    assert registry["privacy"].status == "go"


def test_keywords_shared_with_router() -> None:
    keywords = get_domain_keywords()
    assert "gdpr" in keywords["privacy"]


def test_resolve_domain_for_known_celex() -> None:
    domain = resolve_domain_for_celex("32016R0679")
    assert domain == "privacy"
