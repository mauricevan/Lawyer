"""Tests for engineering knowledge base (plan5 J2)."""
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENGINEERING = _REPO_ROOT / "docs/engineering"


def test_onboarding_pack_exists() -> None:
    assert (_ENGINEERING / "onboarding.md").is_file()
    assert (_ENGINEERING / "runbook-index.md").is_file()
    assert (_ENGINEERING / "troubleshooting.md").is_file()
    assert (_REPO_ROOT / "docs/product/plan5-kpi-scorecard.md").is_file()


def test_knowledge_base_includes_plan6() -> None:
    assert (_REPO_ROOT / "docs/platform/self-service-ops.md").is_file()


def test_critical_components_registered() -> None:
    data = yaml.safe_load((_ENGINEERING / "critical-components.yaml").read_text(encoding="utf-8"))
    ids = {item["id"] for item in data["components"]}
    assert "rag_pipeline" in ids
    assert "auth_security" in ids
