"""Conversation CRUD and dossier management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database import SessionLocal
from backend.src.dependencies.auth import require_permission
from backend.src.security.fastapi_params import ConversationIdPath, TitleQuery
from backend.src.security.rbac_matrix import Permission
from backend.src.services.conversation_service import ConversationService
from shared.schemas.conversation import ConversationSummary, CreateConversationRequest

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(require_permission(Permission.CONVERSATIONS))],
)
service = ConversationService()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.post("", response_model=dict)
async def create_conversation(
    body: CreateConversationRequest,
    session: AsyncSession = Depends(get_db),
) -> dict:
    conv = await service.create(session, body)
    return {"id": str(conv.id), "title": conv.title, "query_mode": conv.query_mode}


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: ConversationIdPath,
    session: AsyncSession = Depends(get_db),
) -> dict:
    conv = await service.get_conversation(session, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Gesprek niet gevonden")
    messages = await service.list_messages(session, conversation_id)
    return {
        "id": str(conv.id),
        "title": conv.title,
        "query_mode": conv.query_mode,
        "is_saved": conv.is_saved,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "citations": m.citations or [],
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


@router.get("")
async def list_conversations(
    saved: bool = False,
    session: AsyncSession = Depends(get_db),
) -> list[ConversationSummary]:
    return await service.list_saved(session, saved_only=saved)


@router.post("/{conversation_id}/save")
async def save_conversation(
    conversation_id: ConversationIdPath,
    title: TitleQuery = None,
    session: AsyncSession = Depends(get_db),
) -> dict:
    await service.save_conversation(session, conversation_id, title)
    return {"status": "saved", "id": conversation_id}


@router.get("/{conversation_id}/share")
async def share_conversation(
    conversation_id: ConversationIdPath,
    session: AsyncSession = Depends(get_db),
) -> dict:
    conv = await service.get_conversation(session, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Gesprek niet gevonden")
    return {
        "permalink": f"/gesprek/{conversation_id}",
        "title": conv.title,
        "shareable": True,
    }
