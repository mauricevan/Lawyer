#!/usr/bin/env python3
"""Policy registry validation gate (plan15 AA)."""
import argparse
import json
from pathlib import Path

from backend.src.services.policy_registry_service import PolicyRegistryService
from backend.src.utils.policy_registry_config import policy_registry_report_path, repo_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Policy registry gate")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    service = PolicyRegistryService()
    payload = service.audit()
    report_path = args.report or (repo_root() / policy_registry_report_path())
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Policy registry gate failed")


if __name__ == "__main__":
    main()
