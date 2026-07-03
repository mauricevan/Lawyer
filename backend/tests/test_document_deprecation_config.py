"""Tests for deprecation register config validation."""
from backend.src.utils.document_deprecation_config import validate_register_payload


def test_validate_register_rejects_invalid_status():
    errors = validate_register_payload({
        "entries": [{"celex": "32014R0330", "status": "active"}],
    })
    assert any("invalid status" in error for error in errors)


def test_validate_register_rejects_duplicate_entries():
    errors = validate_register_payload({
        "entries": [
            {"celex": "32014R0330", "language": "nl", "status": "soft_deprecated"},
            {"celex": "32014R0330", "language": "nl", "status": "retired"},
        ],
    })
    assert any("duplicate" in error for error in errors)
