"""Validate retrieved EUR-Lex chunks before answer generation."""
from typing import Any

from backend.src.services.legal_extractive_generic import can_build_generic_answer
from backend.src.utils.evidence_chunk_filters import (
    chunk_supports_actor,
    filter_substantive_chunks,
)
from backend.src.utils.legal_chunk_text import score_chunk_relevance
from backend.src.utils.conflict_domain_mapping import (
    is_celex_allowed_for_conflict,
    map_conflict_to_domain,
)
from backend.src.utils.domain_framework_registry import celex_from_frameworks
from backend.src.utils.legal_domain_retrieval_filter import (
    filter_chunks_by_domain,
    is_celex_allowed_for_domain,
    rank_chunks_by_domain,
)
from backend.src.utils.legal_question_type_chunk_scoring import rank_chunks_by_question_type
from shared.schemas.evidence_validation import EvidenceFailureReason, EvidenceValidationResult
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import LegalInterpretationPlan

_MIN_RELEVANCE_SCORE = 3


class EvidenceValidationService:
    """Gate answer generation on sufficient legal evidence in retrieved chunks."""

    def validate(
        self,
        question: str,
        chunks: list[dict[str, Any]],
        plan: LegalInterpretationPlan,
        hypothesis: LegalHypothesis | None = None,
    ) -> EvidenceValidationResult:
        """Return PASS only when chunks substantively support the question."""
        if not chunks:
            return self._fail(["no_chunks"])
        conflict_fail = self._conflict_domain_fail(chunks, plan, hypothesis)
        if conflict_fail:
            return conflict_fail
        substantive = filter_substantive_chunks(chunks)
        if not substantive:
            return self._fail(["procedural_only"])
        domain_chunks = filter_chunks_by_domain(substantive, plan.legal_domain)
        if not domain_chunks:
            return self._fail(["domain_mismatch"])
        if self._has_blocked_celex(substantive, plan):
            return self._fail(["domain_mismatch"])
        if not self._actor_supported(domain_chunks, plan.legal_actor, hypothesis):
            return self._fail(["actor_mismatch"])
        if not self._subject_supported(question, domain_chunks, hypothesis):
            return self._fail(["subject_mismatch"])
        ranked = self._rank_validated(domain_chunks, question, plan)
        if not ranked:
            return self._fail(["insufficient_substance"])
        confidence = self._confidence_score(question, ranked[0])
        return EvidenceValidationResult(
            is_valid=True,
            validated_chunks=ranked,
            confidence=confidence,
        )

    def _fail(self, reasons: list[EvidenceFailureReason]) -> EvidenceValidationResult:
        return EvidenceValidationResult(is_valid=False, reasons=reasons)

    def _conflict_domain_fail(
        self,
        chunks: list[dict[str, Any]],
        plan: LegalInterpretationPlan,
        hypothesis: LegalHypothesis | None,
    ) -> EvidenceValidationResult | None:
        """V4 hard-fail when plan or CELEX conflicts with primary legal conflict."""
        if not hypothesis or not hypothesis.primary_legal_conflict:
            return None
        expected = map_conflict_to_domain(hypothesis.primary_legal_conflict).domain
        if plan.legal_domain != expected:
            return self._fail(["domain_mismatch"])
        for chunk in chunks:
            celex = str(chunk.get("celex", "")) or None
            if celex and not is_celex_allowed_for_conflict(celex, hypothesis.primary_legal_conflict):
                return self._fail(["domain_mismatch"])
        return None

    def _has_blocked_celex(
        self,
        chunks: list[dict[str, Any]],
        plan: LegalInterpretationPlan,
    ) -> bool:
        if plan.legal_domain == "unknown":
            return False
        celexes = {str(c.get("celex", "")) for c in chunks if c.get("celex")}
        allowed = [c for c in celexes if is_celex_allowed_for_domain(c, plan.legal_domain)]
        return bool(celexes) and not allowed

    def _actor_supported(
        self,
        chunks: list[dict[str, Any]],
        actor: str,
        hypothesis: LegalHypothesis | None,
    ) -> bool:
        if actor == "unknown":
            return True
        if any(
            chunk_supports_actor(str(chunk.get("text", "")), actor)  # type: ignore[arg-type]
            for chunk in chunks
        ):
            return True
        if hypothesis and hypothesis.legal_problem:
            return any(
                score_chunk_relevance(str(chunk.get("text", "")), hypothesis.legal_problem) >= _MIN_RELEVANCE_SCORE
                for chunk in chunks
            )
        return False

    def _subject_supported(
        self,
        question: str,
        chunks: list[dict[str, Any]],
        hypothesis: LegalHypothesis | None,
    ) -> bool:
        probe = question
        if hypothesis and hypothesis.primary_legal_conflict:
            probe = hypothesis.case_summary or hypothesis.legal_problem
        if can_build_generic_answer(chunks, probe):
            return True
        if hypothesis and self._frameworks_supported(chunks, hypothesis):
            return True
        return any(
            score_chunk_relevance(str(chunk.get("text", "")), probe) >= _MIN_RELEVANCE_SCORE
            for chunk in chunks
        )

    def _frameworks_supported(
        self,
        chunks: list[dict[str, Any]],
        hypothesis: LegalHypothesis,
    ) -> bool:
        expected_celex = celex_from_frameworks(hypothesis.likely_eu_frameworks)
        if expected_celex and any(str(chunk.get("celex")) == expected_celex for chunk in chunks):
            probe = " ".join(hypothesis.likely_eu_frameworks + [hypothesis.legal_problem])
            return any(score_chunk_relevance(str(chunk.get("text", "")), probe) >= 2 for chunk in chunks)
        probe = hypothesis.legal_problem or " ".join(hypothesis.likely_eu_frameworks)
        return any(score_chunk_relevance(str(chunk.get("text", "")), probe) >= _MIN_RELEVANCE_SCORE for chunk in chunks)

    def _rank_validated(
        self,
        chunks: list[dict[str, Any]],
        question: str,
        plan: LegalInterpretationPlan,
    ) -> list[dict[str, Any]]:
        ranked = rank_chunks_by_question_type(
            rank_chunks_by_domain(chunks, plan.legal_domain),
            plan.legal_question_type,
        )
        scored = sorted(
            ranked,
            key=lambda chunk: score_chunk_relevance(str(chunk.get("text", "")), question),
            reverse=True,
        )
        return scored[:8]

    def _confidence_score(self, question: str, best_chunk: dict[str, Any]) -> float:
        relevance = score_chunk_relevance(str(best_chunk.get("text", "")), question)
        return min(1.0, 0.35 + relevance * 0.08)
