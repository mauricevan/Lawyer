#!/usr/bin/env python3
"""Incident playbook and tier-1 alert-runbook audit (plan14 AD)."""
import argparse
import json
from pathlib import Path

from backend.src.services.incident_response_service import IncidentResponseService
from backend.src.utils.alert_runbook_config import incident_audit_report_path, repo_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Incident playbook audit")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    service = IncidentResponseService()
    payload = service.audit()
    report_path = args.report or (repo_root() / incident_audit_report_path())
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Incident playbook audit failed")


if __name__ == "__main__":
    main()
