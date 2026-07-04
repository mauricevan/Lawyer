"""V4 legal reconciliation: validated evidence vs case analysis."""
from typing import Any

from backend.src.services.legal_extractive_generic import can_build_generic_answer
from backend.src.utils.legal_chunk_text import score_chunk_relevance
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult


class LegalReconciliationService:
    """Compare case analysis with validated EUR-Lex chunks before answering."""

    def reconcile(
        self,
        analysis: LegalCaseAnalysis,
        chunks: list[dict[str, Any]],
        evidence: EvidenceValidationResult,
    ) -> ReconciliationResult:
        """Return whether EU sources support the legal hypothesis."""
        if not evidence.is_valid or not chunks:
            return ReconciliationResult(
                conclusion="contradicted",
                rationale="Geen gevalideerde EUR-Lex-bronnen voor deze analyse.",
            )
        probe = f"{analysis.case_summary} {' '.join(analysis.likely_eu_frameworks)}"
        if can_build_generic_answer(chunks, probe):
            return ReconciliationResult(
                conclusion="supported",
                rationale="Bronteksten bevatten operative bepalingen die de analyse ondersteunen.",
            )
        best = max(
            score_chunk_relevance(str(chunk.get("text", "")), probe)
            for chunk in chunks
        )
        if best >= 5:
            return ReconciliationResult(conclusion="supported", rationale="Sterke inhoudelijke overlap met bronnen.")
        if best >= 2:
            return ReconciliationResult(
                conclusion="partially_supported",
                rationale="Beperkte maar relevante ondersteuning in de bronnen.",
            )
        return ReconciliationResult(
            conclusion="contradicted",
            rationale="Bronnen ondersteunen de juridische analyse onvoldoende.",
        )
