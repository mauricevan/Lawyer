"""Unit tests for lifecycle eval gate script (plan13 AD)."""
import json

from backend.src.services.document_version_conflict_service import DocumentVersionConflictService
from backend.scripts import run_lifecycle_eval_gate as gate_module


def test_version_registration_check_passes():
    check = gate_module._run_version_registration_check()
    assert check["name"] == "version_registration"
    assert check["passed"] is True


def test_run_gate_payload_structure(monkeypatch):
    monkeypatch.setattr(gate_module, "_run_deprecation_check", lambda: {"name": "deprecation_register", "passed": True})
    monkeypatch.setattr(
        gate_module,
        "_run_version_registration_check",
        lambda: {"name": "version_registration", "passed": True},
    )

    async def _skip_staleness():
        return {"name": "staleness", "passed": True, "skipped": True}

    monkeypatch.setattr(gate_module, "_run_staleness_check", _skip_staleness)
    payload = __import__("asyncio").run(gate_module.run_gate())
    assert payload["suite"] == "lifecycle_eval_gate"
    assert payload["passed"] is True
    assert len(payload["checks"]) == 3


def test_validate_registered_families_json_serializable():
    result = DocumentVersionConflictService().validate_registered_families()
    json.dumps(result)
