"""Query endpoint with SSE streaming for retrieval status."""
import json
import uuid

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from backend.src.database import SessionLocal
from backend.src.services.conversation_service import ConversationService
from backend.src.services.rag_service import RagService
from shared.schemas.conversation import CreateConversationRequest
from shared.schemas.query import AnswerResponse, QueryRequest

router = APIRouter(tags=["query"])
limiter = Limiter(key_func=get_remote_address)
rag = RagService()
conversations = ConversationService()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.post("/query", response_model=AnswerResponse)
@limiter.limit("20/minute")
async def query(
    request: Request,
    body: QueryRequest,
    session: AsyncSession = Depends(get_db),
) -> AnswerResponse:
    conv_id = body.conversation_id
    if not conv_id:
        conv = await conversations.create(session, CreateConversationRequest(query_mode=body.query_mode))
        conv_id = str(conv.id)
        body.conversation_id = conv_id
    history = await conversations.get_context(session, conv_id)
    response, chunk_ids = await rag.query(body, history)
    response.conversation_id = conv_id
    await conversations.append(session, conv_id, body.question, response, chunk_ids)
    return response


@router.post("/query/stream")
@limiter.limit("20/minute")
async def query_stream(
    request: Request,
    body: QueryRequest,
    session: AsyncSession = Depends(get_db),
):
    conv_id = body.conversation_id
    if not conv_id:
        conv = await conversations.create(session, CreateConversationRequest(query_mode=body.query_mode))
        conv_id = str(conv.id)
        body.conversation_id = conv_id
    history = await conversations.get_context(session, conv_id)

    async def event_generator():
        final_answer = None
        final_citations = []
        async for event in rag.query_with_events(body, history):
            if event.get("step") == "complete":
                detail = event.get("detail", {})
                final_answer = detail.get("answer", "")
                final_citations = detail.get("citations", [])
            yield {"event": event.get("step", "status"), "data": json.dumps(event)}
        if final_answer:
            from shared.schemas.citation import Citation
            citations = [Citation(**c) for c in final_citations]
            answer = AnswerResponse(
                answer=final_answer,
                conversation_id=conv_id,
                citations=citations,
            )
            await conversations.append(session, conv_id, body.question, answer, [])

    return EventSourceResponse(event_generator())
