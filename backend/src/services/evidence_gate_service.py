"""Orchestrate evidence validation and domain-scoped retrieval retry."""
from typing import Any

from backend.src.services.evidence_retrieval_retry_service import EvidenceRetrievalRetryService
from backend.src.services.evidence_validation_service import EvidenceValidationService
from shared.schemas.celex_resolution import CelexResolutionResult
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


class EvidenceGateService:
    """Validate retrieved chunks; retry once within domain before answer generation."""

    def __init__(self) -> None:
        self._validator = EvidenceValidationService()
        self._retry = EvidenceRetrievalRetryService()

    async def gate(
        self,
        request: QueryRequest,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        session: Any | None = None,
        hypothesis: LegalHypothesis | None = None,
        analysis: LegalCaseAnalysis | None = None,
        celex_resolution: CelexResolutionResult | None = None,
    ) -> tuple[AgentFetchResult, EvidenceValidationResult]:
        """Validate evidence; on FAIL retry retrieval once in same domain, then re-validate."""
        evidence = self._validator.validate(request.question, fetch.chunks, plan, hypothesis)
        if evidence.is_valid:
            return self._with_validated_chunks(fetch, evidence), evidence
        retried = await self._retry.retry(
            request, plan, fetch, session, hypothesis, analysis, celex_resolution,
        )
        evidence = self._validator.validate(request.question, retried.chunks, plan, hypothesis)
        if evidence.is_valid:
            return self._with_validated_chunks(retried, evidence), evidence
        return retried, evidence

    def _with_validated_chunks(
        self,
        fetch: AgentFetchResult,
        evidence: EvidenceValidationResult,
    ) -> AgentFetchResult:
        return fetch.model_copy(update={"chunks": evidence.validated_chunks})
