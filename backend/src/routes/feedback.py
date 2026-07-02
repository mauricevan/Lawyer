"""Pilot feedback capture for query quality."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database import SessionLocal
from backend.src.dependencies.auth import require_permission
from backend.src.models.tables import QueryFeedback
from backend.src.security.rbac_matrix import Permission
from shared.schemas.feedback import FeedbackRequest

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    dependencies=[Depends(require_permission(Permission.FEEDBACK))],
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.post("")
async def submit_feedback(body: FeedbackRequest, session: AsyncSession = Depends(get_db)) -> dict[str, str]:
    session.add(QueryFeedback(
        conversation_id=body.conversation_id,
        rating=body.rating,
        category=body.category,
        comment=body.comment,
    ))
    await session.commit()
    return {"status": "received"}
