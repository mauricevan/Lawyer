"""Atomic publish gate — fail-fast only, no strip or repair."""
from datetime import datetime, timezone

from backend.src.utils.explanation_authority_guard import has_authority_leak
from shared.schemas.legal_explanation import (
    ExplanationSections,
    GapReason,
    GapResponse,
    LegalExplanationDraft,
    PublishedExplanation,
    SafePartialKnowledge,
)


class ExplanationPublishGuardService:
    """Promote draft to PublishedExplanation or deterministic GapResponse."""

    def publish(self, draft: LegalExplanationDraft) -> PublishedExplanation | GapResponse:
        if draft.coverage_status == "clarify_only":
            leak = self._authority_violation(draft)
            if leak:
                return self._validation_gap(draft, leak)
            return PublishedExplanation(
                draft=draft,
                published_at=datetime.now(timezone.utc),
            )
        leak = self._authority_violation(draft)
        if leak:
            return self._validation_gap(draft, leak)
        if draft.coverage_status != "adequate":
            return self._retrieval_gap(draft)
        if not draft.citations:
            return self._citation_gap(draft)
        return PublishedExplanation(
            draft=draft,
            published_at=datetime.now(timezone.utc),
        )

    def _authority_violation(self, draft: LegalExplanationDraft) -> str | None:
        for field in ExplanationSections.model_fields:
            text = getattr(draft.sections, field)
            if text and has_authority_leak(text):
                return field
        return None

    def _validation_gap(self, draft: LegalExplanationDraft, field: str) -> GapResponse:
        return GapResponse(
            reason=GapReason.validation_failure,
            sections=_gap_sections(),
            safe_partial=SafePartialKnowledge(
                factual_gaps=(f"Blocked field: {field}",),
            ),
            quality=draft.quality,
            coverage_guidance=draft.coverage_guidance,
        )

    def _retrieval_gap(self, draft: LegalExplanationDraft) -> GapResponse:
        return GapResponse(
            reason=GapReason.retrieval_failure,
            sections=_gap_sections_from_draft(draft),
            quality=draft.quality,
            coverage_guidance=draft.coverage_guidance,
            citations=draft.citations,
        )

    def _citation_gap(self, draft: LegalExplanationDraft) -> GapResponse:
        return GapResponse(
            reason=GapReason.citation_failure,
            sections=_gap_sections_from_draft(draft),
            quality=draft.quality,
            coverage_guidance=draft.coverage_guidance,
        )


def _gap_sections() -> ExplanationSections:
    return ExplanationSections(
        short_answer=(
            "Ik kan op basis van de beschikbare EU-bronnen geen betrouwbaar antwoord geven."
        ),
        law_says="",
        practical_meaning="",
        legal_sources="",
        uncertainties="Het antwoord voldeed niet aan de publicatie-eisen.",
        disclaimer=(
            "Algemene informatie op basis van EUR-Lex. Geen persoonlijk juridisch advies."
        ),
    )


def _gap_sections_from_draft(draft: LegalExplanationDraft) -> ExplanationSections:
    if draft.sections.short_answer.strip():
        return draft.sections
    return _gap_sections()
