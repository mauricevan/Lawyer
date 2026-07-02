"""Tests for dataset registry loader (plan7 N)."""
from ingestion.src.data.dataset_registry_loader import get_registry_version, load_dataset_registry


def test_registry_loads_curated_corpus() -> None:
    registry = load_dataset_registry()
    assert "curated_corpus" in registry
    assert registry["curated_corpus"].owner == "product"


def test_registry_version_present() -> None:
    version = get_registry_version()
    assert version.startswith("2026")


def test_eval_fixtures_registered() -> None:
    registry = load_dataset_registry()
    assert "eval_questions_nl" in registry
    assert registry["eval_questions_nl"].path.endswith("rag_eval_questions.json")
