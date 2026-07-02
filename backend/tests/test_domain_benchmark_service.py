"""Tests for domain benchmark go/no-go logic."""
from backend.src.services.domain_benchmark_service import DomainBenchmarkService
from ingestion.src.data.domain_registry_loader import load_domain_registry


def test_go_domain_passes_at_threshold() -> None:
    service = DomainBenchmarkService()
    rows = [{"recall_at_5": 1.0, "mrr": 1.0}, {"recall_at_5": 0.8, "mrr": 0.5}]
    result = service.evaluate_domain("privacy", rows, load_domain_registry())
    assert result["decision"] == "pass"


def test_no_go_domain_is_blocked() -> None:
    service = DomainBenchmarkService()
    rows = [{"recall_at_5": 1.0, "mrr": 1.0}]
    result = service.evaluate_domain("competition", rows, load_domain_registry())
    assert result["decision"] == "blocked"
