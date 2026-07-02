"""Tests for plan6 platform artifacts."""
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]


def test_env_parity_matrix_loads() -> None:
    path = _REPO / "docs/platform/env-parity-matrix.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert len(data["required_all"]) >= 5


def test_env_example_has_required_keys() -> None:
    matrix = yaml.safe_load((_REPO / "docs/platform/env-parity-matrix.yaml").read_text(encoding="utf-8"))
    keys = {
        line.split("=", 1)[0].strip()
        for line in (_REPO / ".env.example").read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.strip().startswith("#")
    }
    for key in matrix["required_all"]:
        assert key in keys


def test_self_service_docs_and_templates_exist() -> None:
    assert (_REPO / "docs/platform/self-service-ops.md").is_file()
    assert (_REPO / "docs/engineering/templates/service_module/service.py.template").is_file()
    assert (_REPO / "scripts/platform/run-self-service.sh").is_file()
