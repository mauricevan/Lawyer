"""Partner API routes — tenant-isolated channel (plan31 AA)."""
from fastapi import APIRouter, Depends

from backend.src.dependencies.partner_auth import require_partner
from backend.src.services.partner_api_service import PartnerContext, PartnerApiService

router = APIRouter(prefix="/partner", tags=["partner"])
_service = PartnerApiService()


@router.get("/status")
async def partner_status(partner: PartnerContext = Depends(require_partner)) -> dict:
    return {
        "partner_id": partner.partner_id,
        "tier": partner.tier,
        "rate_limit_rpm": partner.rate_limit_rpm,
        "status": "ok",
    }


@router.get("/policy")
async def partner_policy_snapshot(partner: PartnerContext = Depends(require_partner)) -> dict:
    return {"partner_id": partner.partner_id, "audit": _service.audit()}
