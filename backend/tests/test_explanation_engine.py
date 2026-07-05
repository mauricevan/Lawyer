"""Tests for explanation engine publish/render pipeline."""
from backend.src.services.explanation_publish_guard_service import ExplanationPublishGuardService
from backend.src.services.explanation_renderer_service import ExplanationRendererService
from backend.src.utils.explanation_section_mapper import markdown_to_sections, sections_to_markdown
from shared.schemas.citation import Citation
from shared.schemas.legal_explanation import (
    ExplanationSections,
    GapReason,
    LegalExplanationDraft,
    PublishedExplanation,
)


def _draft(text: str, status: str = "adequate", with_citation: bool = True) -> LegalExplanationDraft:
    sections = markdown_to_sections(text, "Disclaimer text")
    citations = (
        (Citation(celex="32022R2065", article="5", excerpt="x", eurlex_url="https://eur-lex.europa.eu/"),)
        if with_citation
        else ()
    )
    return LegalExplanationDraft(
        sections=sections,
        citations=citations,
        coverage_status=status,  # type: ignore[arg-type]
        retrieval_context_id="ctx-1",
        quality={"confidence_score": 0.8, "verification_questions": []},
    )


def test_publish_passes_clean_draft() -> None:
    text = (
        "## Kort antwoord\nHet hangt af van uw situatie.\n\n"
        "## Juridische basis\nArtikel 5 DSA regelt transparantie.\n\n"
        "## Let op\nGeen advies."
    )
    outcome = ExplanationPublishGuardService().publish(_draft(text))
    assert isinstance(outcome, PublishedExplanation)


def test_publish_blocks_authority_leak() -> None:
    text = "## Kort antwoord\nOK\n\n## Hof-simulatie\nIssue"
    outcome = ExplanationPublishGuardService().publish(_draft(text))
    assert outcome.reason == GapReason.validation_failure  # type: ignore[attr-defined]


def test_renderer_is_deterministic() -> None:
    sections = ExplanationSections(
        short_answer="Ja, onder voorwaarden.",
        law_says="Artikel 5.",
        practical_meaning="U moet transparant zijn.",
        legal_sources="DSA art. 5",
        uncertainties="Geen.",
        disclaimer="Geen advies.",
    )
    published = PublishedExplanation(
        draft=LegalExplanationDraft(
            sections=sections,
            citations=(),
            coverage_status="adequate",
            retrieval_context_id="x",
        ),
        published_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    renderer = ExplanationRendererService()
    a = renderer.render_published(published)
    b = renderer.render_published(published)
    assert a == b
    assert "## Kort antwoord" in a
    assert sections_to_markdown(sections) == a


def test_clarify_only_publishes_without_citations() -> None:
    text = (
        "## Kort antwoord\nWat voor platform bedoelt u?\n\n"
        "## Disclaimer\nGeen advies."
    )
    draft = LegalExplanationDraft(
        sections=markdown_to_sections(text, "Geen advies."),
        citations=(),
        coverage_status="clarify_only",
        retrieval_context_id="ctx-clarify",
        quality={"confidence_score": 0.0, "verification_questions": ["app / SaaS", "contentwebsite"]},
    )
    outcome = ExplanationPublishGuardService().publish(draft)
    assert isinstance(outcome, PublishedExplanation)
    assert outcome.draft.coverage_status == "clarify_only"


def test_insufficient_draft_returns_gap() -> None:
    text = "## Kort antwoord\nIk kan geen antwoord geven."
    outcome = ExplanationPublishGuardService().publish(_draft(text, status="insufficient", with_citation=False))
    assert outcome.reason == GapReason.retrieval_failure  # type: ignore[attr-defined]
