"""Tests for cycle plan gates (plan16–plan30)."""
import pytest

from backend.src.services.cycle_plan_gate_service import CyclePlanGateService


@pytest.mark.parametrize("plan_id", [f"plan{n}" for n in range(16, 31)])
def test_cycle_plan_gate_passes(plan_id: str) -> None:
    report = CyclePlanGateService().audit_plan(plan_id)
    assert report["passed"], report


def test_all_cycle_plans_gate_passes() -> None:
    report = CyclePlanGateService().audit_all()
    assert report["passed"]
    assert report["passed_count"] == 15
