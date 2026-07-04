"""Build AnswerResponse from SSE complete event detail."""
from typing import Any

from shared.legal.disclaimers import get_disclaimer
from shared.schemas.citation import Citation
from shared.schemas.coverage_guidance import CoverageGuidance
from shared.schemas.query import AnswerResponse


def answer_from_stream_detail(
    detail: dict[str, Any],
    conv_id: str,
    audience: str = "layperson",
    language: str = "nl",
) -> AnswerResponse:
    """Map stream `complete` payload fields onto AnswerResponse for persistence."""
    citations = [Citation(**c) for c in detail.get("citations", [])]
    guidance_raw = detail.get("coverage_guidance")
    guidance = CoverageGuidance(**guidance_raw) if guidance_raw else None
    return AnswerResponse(
        answer=str(detail.get("answer", "")),
        conversation_id=conv_id,
        citations=citations,
        disclaimer=detail.get("disclaimer") or get_disclaimer(audience, language),  # type: ignore[arg-type]
        retrieval_route=detail.get("retrieval_route"),
        confidence_score=detail.get("confidence_score"),
        verification_questions=list(detail.get("verification_questions") or []),
        coverage_guidance=guidance,
        coverage_status=detail.get("coverage_status"),
    )
