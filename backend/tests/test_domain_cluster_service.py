"""Tests for domain clustering on ambiguous router output."""
from backend.src.models.query_route import QueryRoute
from backend.src.services.domain_cluster_service import DomainClusterService


def test_cluster_picks_best_when_multiple_domains():
    service = DomainClusterService()
    route = QueryRoute(domains=["finance", "sustainability"], confidence=0.55)
    enriched = service.enrich("Wat zegt CSRD over bankrapportage?", route, 0.55)
    assert len(enriched.domains) == 1
    assert enriched.domains[0] in {"finance", "sustainability"}
    assert enriched.domain_cluster is not None


def test_cluster_skips_domain_lock_when_low_confidence():
    service = DomainClusterService()
    route = QueryRoute(domains=[], confidence=0.4)
    enriched = service.enrich("Algemene vraag over EU wetgeving", route, 0.55)
    assert enriched.domains == []
    assert enriched.confidence < 0.55
