#!/usr/bin/env python3
"""Partner API policy gate (plan31 AA)."""
import json

from backend.src.services.partner_api_service import PartnerApiService
from backend.src.utils.partner_api_config import load_partner_api_policy

_REPO = __import__("pathlib").Path(__file__).resolve().parents[2]


def main() -> None:
    payload = PartnerApiService().audit()
    rel = load_partner_api_policy().get("report", {}).get("path", "")
    if rel:
        path = _REPO / str(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Partner API gate failed")


if __name__ == "__main__":
    main()
