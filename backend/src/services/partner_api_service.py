"""Partner API key resolution and tenant isolation (plan31 AA)."""
import os
from dataclasses import dataclass
from typing import Any

from backend.src.utils.partner_api_config import load_partner_api_policy


@dataclass(slots=True)
class PartnerContext:
    partner_id: str
    tier: str
    rate_limit_rpm: int


class PartnerApiService:
    """Resolves partner API keys and enforces tenant isolation policy."""

    def __init__(self) -> None:
        self._policy = load_partner_api_policy()

    def resolve_partner(self, api_key: str) -> PartnerContext | None:
        if not api_key.strip():
            return None
        for entry in self._policy.get("partners", []):
            expected = self._key_for_partner(entry)
            if expected and api_key == expected:
                return PartnerContext(
                    partner_id=str(entry["id"]),
                    tier=str(entry.get("tier", "sandbox")),
                    rate_limit_rpm=int(entry.get("rate_limit_rpm", 60)),
                )
        return None

    def audit(self) -> dict[str, Any]:
        partners = self._policy.get("partners", [])
        configured = sum(1 for entry in partners if self._key_for_partner(entry))
        isolation = self._policy.get("tenant_isolation", {})
        passed = bool(isolation.get("enabled")) and isolation.get("mode") == "api_key"
        return {
            "suite": "partner_api",
            "passed": passed,
            "partner_count": len(partners),
            "configured_keys": configured,
            "tenant_isolation": isolation,
        }

    def summarize_admin(self) -> dict[str, Any]:
        audit = self.audit()
        return {
            "partner_count": audit["partner_count"],
            "configured_keys": audit["configured_keys"],
            "tenant_isolation_enabled": audit["tenant_isolation"].get("enabled", False),
        }

    def _key_for_partner(self, entry: dict[str, Any]) -> str:
        env_name = str(entry.get("api_key_env", ""))
        if not env_name:
            return ""
        return os.getenv(env_name, "").strip()
