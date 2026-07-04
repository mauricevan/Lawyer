"""Tests for V6 legal effect answer framing."""
from backend.src.services.legal_effect_answer_service import enrich_layperson_answer
from shared.schemas.legal_effect import LegalEffectAnalysis


def test_enrich_inserts_juridisch_effect_section():
    effect = LegalEffectAnalysis(
        legal_effect_type="discrimination_by_establishment",
        restriction_strength="high",
        state_action="eligibility_requirement",
        effect_conclusion_hint="prohibited",
    )
    raw = "## Kort antwoord\nOude tekst.\n\n## Juridische basis\nArtikel 3."
    enriched = enrich_layperson_answer(raw, effect)
    assert "## Juridisch effect" in enriched
    assert "In beginsel niet toegestaan" in enriched
    assert "## Juridische basis" in enriched
