"""Tests for project completion service (plan31 AC)."""
from backend.src.services.project_completion_service import ProjectCompletionService


def test_project_completion_scripts_exist():
    service = ProjectCompletionService()
    assert service._scripts_exist()  # noqa: SLF001


def test_project_completion_audit_when_reports_present():
    report = ProjectCompletionService().audit()
    assert "gates" in report
    assert report["scripts_ok"] is True
