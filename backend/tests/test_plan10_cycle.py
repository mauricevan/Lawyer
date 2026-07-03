"""Tests for plan10 cycle planning artifacts."""
from pathlib import Path

import yaml

from backend.src.services.cycle_planning_service import CyclePlanningService
from backend.src.services.kpi_catalog_service import KpiCatalogService

_REPO = Path(__file__).resolve().parents[2]


def test_kpi_catalog_has_leading_and_lagging() -> None:
    service = KpiCatalogService()
    assert not service.validate_catalog()
    assert len(service.leading_indicators()) >= 2
    assert len(service.lagging_indicators()) >= 2


def test_cycle_planning_loads_legacy_register() -> None:
    service = CyclePlanningService()
    data = service.load_legacy_register()
    assert len(data.get("items", [])) >= 2


def test_next_cycle_themes_prioritized() -> None:
    data = yaml.safe_load((_REPO / "docs/cycle/next-cycle-themes.yaml").read_text(encoding="utf-8"))
    themes = data["themes"]
    assert themes[0]["priority"] == 1


def test_plan10_scripts_exist() -> None:
    scripts = [
        "scripts/ops/run-cycle-planning-review.sh",
        "scripts/ops/run-kpi-catalog-review.sh",
        "scripts/ops/run-plan-transition-check.sh",
    ]
    for script in scripts:
        assert (_REPO / script).is_file()


def test_plan11_kickoff_approved() -> None:
    text = (_REPO / "docs/cycle/plan11-kickoff.md").read_text(encoding="utf-8")
    assert "APPROVED" in text


def test_plan12_kickoff_approved() -> None:
    text = (_REPO / "docs/cycle/plan12-kickoff.md").read_text(encoding="utf-8")
    assert "APPROVED" in text


def test_plan13_kickoff_approved() -> None:
    text = (_REPO / "docs/cycle/plan13-kickoff.md").read_text(encoding="utf-8")
    assert "APPROVED" in text


def test_plan13_transition_is_historical() -> None:
    service = CyclePlanningService()
    assert service.validate_plan_transition("plan13")


def test_plan14_kickoff_approved() -> None:
    text = (_REPO / "docs/cycle/plan14-kickoff.md").read_text(encoding="utf-8")
    assert "APPROVED" in text


def test_plan14_transition_is_historical() -> None:
    service = CyclePlanningService()
    assert service.validate_plan_transition("plan14")


def test_plan15_kickoff_approved() -> None:
    text = (_REPO / "docs/cycle/plan15-kickoff.md").read_text(encoding="utf-8")
    assert "APPROVED" in text


def test_plan15_transition_is_historical() -> None:
    service = CyclePlanningService()
    assert service.validate_plan_transition("plan15")


def test_plan30_transition_validates() -> None:
    service = CyclePlanningService()
    assert not service.validate_plan_transition("plan30")


def test_plan30_series_closed() -> None:
    text = (_REPO / "docs/cycle/plan30-exit-review.md").read_text(encoding="utf-8")
    assert "APPROVED" in text
