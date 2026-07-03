"""Query endpoint with SSE streaming for retrieval status."""
import json
import logging
import time
import uuid

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from backend.src.database import SessionLocal
from backend.src.dependencies.auth import Principal, get_current_principal, require_permission
from backend.src.security.rbac_matrix import Permission
from backend.src.services.audit_service import AuditService
from backend.src.services.conversation_service import ConversationService
from backend.src.services.guardrails_service import GuardrailsService
from backend.src.services.metrics_service import metrics_service
from backend.src.services.query_cache_service import QueryCacheService
from backend.src.services.rag_service import RagService
from backend.src.utils.query_filter_sanitizer import sanitize_query_request
from shared.schemas.conversation import CreateConversationRequest
from shared.schemas.query import AnswerResponse, QueryRequest

router = APIRouter(tags=["query"])
limiter = Limiter(key_func=get_remote_address)
rag = RagService()
conversations = ConversationService()
audit_service = AuditService()
cache_service = QueryCacheService()
guardrails = GuardrailsService()
logger = logging.getLogger(__name__)


def _enforce_guardrails(question: str) -> None:
    hits = guardrails.check_question(question)
    if hits:
        metrics_service.record_injection_flag()
    guardrails.enforce_question(question)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def _prepare_conversation(
    session: AsyncSession,
    body: QueryRequest,
) -> str:
    conv_id = body.conversation_id
    if not conv_id:
        conv = await conversations.create(session, CreateConversationRequest(query_mode=body.query_mode))
        conv_id = str(conv.id)
        body.conversation_id = conv_id
    return conv_id


@router.post("/query", response_model=AnswerResponse, dependencies=[Depends(require_permission(Permission.QUERY))])
@limiter.limit("20/minute")
async def query(
    request: Request,
    body: QueryRequest,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> AnswerResponse:
    started_at = time.perf_counter()
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    body = sanitize_query_request(body, principal.role)
    _enforce_guardrails(body.question)
    metrics_service.record_query(is_stream=False)
    conv_id = await _prepare_conversation(session, body)
    history = await conversations.get_context(session, conv_id)
    response, chunk_ids, retrieval_chunks = await rag.query(body, history, session=session)
    response.conversation_id = conv_id
    latency_ms = int((time.perf_counter() - started_at) * 1000)
    in_force = body.filters.in_force_only if body.filters else True
    query_hash = cache_service.build_key(body.question, body.language, in_force, body.filters)
    await cache_service.track_live_chunks(
        session,
        query_hash=query_hash,
        chunks=retrieval_chunks,
    )
    await audit_service.log_query(
        session=session,
        request_id=request_id,
        conversation_id=conv_id,
        question=body.question,
        route={
            "filters": body.filters.model_dump() if body.filters else None,
            "retrieval_route": response.retrieval_route,
        },
        chunk_ids=chunk_ids,
        latency_ms=latency_ms,
    )
    await conversations.append(session, conv_id, body.question, response, chunk_ids)
    await session.commit()
    return response


@router.post("/query/stream", dependencies=[Depends(require_permission(Permission.QUERY))])
@limiter.limit("20/minute")
async def query_stream(
    request: Request,
    body: QueryRequest,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    started_at = time.perf_counter()
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    body = sanitize_query_request(body, principal.role)
    _enforce_guardrails(body.question)
    metrics_service.record_query(is_stream=True)
    conv_id = await _prepare_conversation(session, body)
    history = await conversations.get_context(session, conv_id)

    async def event_generator():
        final_answer = None
        final_citations = []
        retrieval_route = None
        retrieval_chunks: list[dict] = []
        chunk_ids: list[str] = []
        async for event in rag.query_with_events(body, history, session=session):
            event.setdefault("detail", {})
            event["detail"]["request_id"] = request_id
            if event.get("step") == "found":
                detail = event.get("detail", {})
                retrieval_route = detail.get("retrieval_route")
                retrieval_chunks = detail.get("retrieval_chunks", [])
                chunk_ids = detail.get("chunk_ids", [])
            if event.get("step") == "complete":
                detail = event.get("detail", {})
                final_answer = detail.get("answer", "")
                final_citations = detail.get("citations", [])
                retrieval_route = detail.get("retrieval_route", retrieval_route)
            yield {"event": event.get("step", "status"), "data": json.dumps(event)}
        if final_answer:
            from shared.schemas.citation import Citation
            citations = [Citation(**c) for c in final_citations]
            answer = AnswerResponse(
                answer=final_answer,
                conversation_id=conv_id,
                citations=citations,
                retrieval_route=retrieval_route,
            )
            await conversations.append(session, conv_id, body.question, answer, chunk_ids)
            in_force = body.filters.in_force_only if body.filters else True
            query_hash = cache_service.build_key(body.question, body.language, in_force, body.filters)
            await cache_service.track_live_chunks(session, query_hash=query_hash, chunks=retrieval_chunks)
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            await audit_service.log_query(
                session=session,
                request_id=request_id,
                conversation_id=conv_id,
                question=body.question,
                route={"filters": body.filters.model_dump() if body.filters else None, "retrieval_route": retrieval_route},
                chunk_ids=chunk_ids,
                latency_ms=latency_ms,
            )
            await session.commit()

    return EventSourceResponse(event_generator())
