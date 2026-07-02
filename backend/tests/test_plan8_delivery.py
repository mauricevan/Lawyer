"""Tests for plan8 delivery and org artifacts."""
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]


def test_ownership_matrix_loads() -> None:
    data = yaml.safe_load((_REPO / "docs/org/component-ownership-matrix.yaml").read_text(encoding="utf-8"))
    ids = {item["id"] for item in data["components"]}
    assert "rag_pipeline" in ids
    assert "ingest_pipeline" in ids


def test_interface_slas_define_query_api() -> None:
    data = yaml.safe_load((_REPO / "docs/org/interface-slas.yaml").read_text(encoding="utf-8"))
    assert "query_api" in data["interfaces"]


def test_quality_gates_reference_scripts() -> None:
    data = yaml.safe_load((_REPO / "docs/engineering/quality-gates.yaml").read_text(encoding="utf-8"))
    script = data["gates"]["knowledge_base"]["script"]
    assert (_REPO / script).is_file()


def test_plan8_playbooks_exist() -> None:
    base = _REPO / "docs/engineering/playbooks"
    assert (base / "release.md").is_file()
    assert (base / "first-contribution.md").is_file()


def test_definition_of_done_exists() -> None:
    assert (_REPO / "docs/engineering/definition-of-done.md").is_file()
    assert (_REPO / "docs/engineering/release-standards.md").is_file()
