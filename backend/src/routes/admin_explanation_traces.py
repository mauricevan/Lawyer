"""Admin API for read-only explanation telemetry traces."""
from fastapi import APIRouter, Depends, HTTPException

from backend.src.dependencies.auth import require_permission
from backend.src.security.fastapi_params import PageLimit
from backend.src.security.rbac_matrix import Permission
from backend.src.services.internal_trace_store_service import internal_trace_store

router = APIRouter(prefix="/admin/explanation-traces", tags=["admin-explanation-traces"])


@router.get("", dependencies=[Depends(require_permission(Permission.ADMIN_READ))])
async def list_explanation_traces(limit: PageLimit = 20) -> dict:
    traces = internal_trace_store.list_recent(limit=limit)
    return {
        "count": len(traces),
        "items": [trace.model_dump(mode="json") for trace in traces],
    }


@router.get("/{trace_id}", dependencies=[Depends(require_permission(Permission.ADMIN_READ))])
async def get_explanation_trace(trace_id: str) -> dict:
    trace = internal_trace_store.get(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace.model_dump(mode="json")
