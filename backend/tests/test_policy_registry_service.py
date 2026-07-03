"""Unit tests for policy registry validation (plan15 AA)."""
from pathlib import Path

from backend.src.services.policy_registry_service import PolicyRegistryService


def test_policy_registry_gate_passes():
    report = PolicyRegistryService().audit()
    assert report["passed"], report["issues"]


def test_policy_registry_coverage_meets_kpi():
    coverage = PolicyRegistryService().build_coverage()
    assert coverage["coverage_ratio"] >= 0.95
    assert coverage["valid_count"] == coverage["registered_count"]


def test_summarize_admin_lists_registered_policies():
    summary = PolicyRegistryService().summarize_admin()
    assert summary["registered_count"] >= 9
    assert summary["invalid_policies"] == []


def test_invalid_policy_detected(tmp_path: Path):
    registry = tmp_path / "policy_registry.yaml"
    policy = tmp_path / "broken.yaml"
    policy.write_text("version: '1'\n", encoding="utf-8")
    registry.write_text(
        """
version: "1"
gate:
  min_coverage_ratio: 0.95
  require_version_field: true
policies:
  - id: broken
    path: broken.yaml
    domain: test
    plan: plan15
    required_keys: [missing_key]
""".strip(),
        encoding="utf-8",
    )
    service = PolicyRegistryService(root=tmp_path)
    service._registry = __import__("yaml").safe_load(registry.read_text(encoding="utf-8"))
    row = service._validate_entry(service._registry["policies"][0])
    assert row["valid"] is False
