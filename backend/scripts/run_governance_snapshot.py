#!/usr/bin/env python3
"""Governance snapshot gate (plan15 AD)."""
import json

from backend.src.services.governance_report_service import GovernanceReportService


def main() -> None:
    service = GovernanceReportService()
    payload = service.audit()
    path = service.write_report(payload)
    print(json.dumps(payload, indent=2))
    print(f"→ Report: {path.relative_to(path.parents[3])}")
    if not payload.get("passed"):
        raise SystemExit("Governance snapshot gate failed")


if __name__ == "__main__":
    main()
