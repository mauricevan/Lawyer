"""Extractive-first answer bundles from retrieved EU chunks."""
from typing import Any

from backend.src.services.answer_bundle_assembly_service import AnswerBundleAssemblyService
from backend.src.services.legal_extractive_answer_service import LegalExtractiveAnswerService
from backend.src.services.legal_extractive_generic import can_build_generic_answer
from backend.src.services.source_consistency_service import SourceConsistencyService
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.query import QueryRequest


class AnswerExtractiveBundleService:
    """Build adequate answers directly from operative legal chunks."""

    def __init__(self) -> None:
        self._extractive = LegalExtractiveAnswerService()
        self._assembly = AnswerBundleAssemblyService()
        self._source_consistency = SourceConsistencyService()

    def try_build(
        self,
        request: QueryRequest,
        chunks: list[dict[str, Any]],
        retrieval_route: str | None,
    ) -> dict[str, Any] | None:
        if not can_build_generic_answer(chunks, request.question):
            if self._extractive.count_usable_excerpts(chunks, request.question) < 1:
                return None
        if request.audience == "professional":
            answer_text = self._extractive.build_professional_answer(request.question, chunks)
        else:
            answer_text = self._extractive.build_layperson_answer(request.question, chunks)
        if not answer_text:
            return None
        citations = self._source_consistency.filter_citations([], chunks)
        return self._assembly.finalize(
            request,
            answer_text,
            citations,
            chunks,
            retrieval_route or "extractive",
            AdequacyResult(is_adequate=True, coverage_status="adequate"),
            None,
        )
