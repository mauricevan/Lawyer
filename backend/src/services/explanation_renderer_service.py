"""Dumb template renderer — no inference, no LLM imports."""
from shared.schemas.legal_explanation import (
    ExplanationEngineResult,
    GapResponse,
    PublishedExplanation,
)
from backend.src.utils.explanation_section_mapper import sections_to_markdown


class ExplanationRendererService:
    """Pure presentation: frozen sections → markdown."""

    def render_published(self, published: PublishedExplanation) -> str:
        return sections_to_markdown(published.draft.sections)

    def render_gap(self, gap: GapResponse) -> str:
        return sections_to_markdown(gap.sections)

    def to_engine_result(
        self,
        published: PublishedExplanation | None,
        gap: GapResponse | None,
    ) -> ExplanationEngineResult:
        if published:
            return ExplanationEngineResult(
                answer_markdown=self.render_published(published),
                published=published,
                citations=published.draft.citations,
                disclaimer=published.draft.sections.disclaimer,
                coverage_status=published.draft.coverage_status,
                quality=published.draft.quality,
                coverage_guidance=published.draft.coverage_guidance,
                retrieval_context_id=published.draft.retrieval_context_id,
            )
        assert gap is not None
        return ExplanationEngineResult(
            answer_markdown=self.render_gap(gap),
            gap=gap,
            citations=gap.citations,
            disclaimer=gap.sections.disclaimer,
            coverage_status="insufficient",
            quality=gap.quality,
            coverage_guidance=gap.coverage_guidance,
        )
