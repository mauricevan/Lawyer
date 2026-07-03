"""Tests for plan11 AB employment domain go-live."""
import json
from pathlib import Path

import yaml

from backend.scripts.build_eval_fixture import build_questions
from ingestion.src.data.domain_registry_loader import load_domain_registry

_REPO = Path(__file__).resolve().parents[2]


def test_employment_domain_is_go() -> None:
    registry = load_domain_registry()
    employment = registry["employment"]
    assert employment.status == "go"
    assert len(employment.seed_celex) >= 3


def test_eval_fixture_includes_employment_seeds() -> None:
    rows = build_questions(limit=100)
    employment_celex = set(load_domain_registry()["employment"].seed_celex)
    covered = {row["expected_celex"][0] for row in rows if row.get("domain") == "employment"}
    assert employment_celex.issubset(covered)


def test_employment_cluster_in_curated() -> None:
    data = yaml.safe_load(
        (_REPO / "ingestion/src/data/curated_celex.yaml").read_text(encoding="utf-8")
    )
    cluster = data["clusters"]["employment_law"]
    assert "32003L0088" in cluster
    assert "32008L0104" in cluster
