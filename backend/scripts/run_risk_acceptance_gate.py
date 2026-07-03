#!/usr/bin/env python3
"""Risk acceptance register gate (plan15 AB)."""
import argparse
import json
from pathlib import Path

from backend.src.services.risk_acceptance_service import RiskAcceptanceService
from backend.src.utils.risk_acceptance_config import load_risk_acceptance_register, repo_root


def main() -> None:
    service = RiskAcceptanceService()
    payload = service.audit()
    rel = load_risk_acceptance_register().get("report", {}).get("path", "")
    path = repo_root() / str(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Risk acceptance gate failed")


if __name__ == "__main__":
    main()
