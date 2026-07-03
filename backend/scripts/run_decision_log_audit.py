#!/usr/bin/env python3
"""Decision log audit gate (plan15 AC)."""
import json

from backend.src.services.decision_log_service import DecisionLogService
from backend.src.utils.decision_log_config import load_decision_log_index, repo_root


def main() -> None:
    service = DecisionLogService()
    payload = service.audit()
    rel = load_decision_log_index().get("report", {}).get("path", "")
    path = repo_root() / str(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Decision log audit failed")


if __name__ == "__main__":
    main()
