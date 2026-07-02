"""Tests for plan11 AA multilingual corpus artifacts."""
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]


def test_multilingual_seed_registered() -> None:
    registry = yaml.safe_load(
        (_REPO / "ingestion/src/data/dataset_registry.yaml").read_text(encoding="utf-8")
    )
    assert "multilingual_seed" in registry["datasets"]


def test_terminology_glossary_has_core_terms() -> None:
    data = yaml.safe_load(
        (_REPO / "docs/product/terminology-glossary.yaml").read_text(encoding="utf-8")
    )
    assert "gdpr" in data["terms"]
    assert "fr" in data["terms"]["gdpr"]


def test_ingest_script_exists() -> None:
    assert (_REPO / "ingestion/scripts/ingest_multilingual_seed.py").is_file()
    assert (_REPO / "scripts/qa/run-ingest-multilingual-seed.sh").is_file()
