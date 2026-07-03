"""Partner API authentication dependency (plan31 AA)."""
from fastapi import Header, HTTPException, status

from backend.src.services.partner_api_service import PartnerApiService, PartnerContext

_partner_service = PartnerApiService()


async def require_partner(
    x_partner_key: str | None = Header(default=None, alias="X-Partner-Key"),
) -> PartnerContext:
    if not x_partner_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Partner key required")
    partner = _partner_service.resolve_partner(x_partner_key)
    if partner is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid partner key")
    return partner
