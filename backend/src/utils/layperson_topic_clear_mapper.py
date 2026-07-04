"""Map layperson topic YAML matches to LaypersonClearAnswer."""
from shared.schemas.layperson_clear_answer import (
    ArticleSummary,
    LaypersonClearAnswer,
    ObligationRow,
    TermDefinition,
)

from backend.src.services.layperson_topic_service import LaypersonTopicMatch

_DEFAULT_LET_OP = (
    "Dit is geen persoonlijk juridisch advies. Raadpleeg een jurist of bevoegde "
    "instantie voor uw specifieke situatie."
)


def topic_match_to_clear_answer(match: LaypersonTopicMatch) -> LaypersonClearAnswer:
    """Convert topic match (legacy or extended YAML) to structured answer."""
    obligations = _obligations_from_match(match)
    basis = _legal_basis_from_match(match)
    return LaypersonClearAnswer(
        kort_antwoord=match.short_answer_nl,
        obligations=obligations,
        voorbeeld=match.example_nl or match.practical_nl,
        juridische_basis=basis,
        begrippen=_terms_from_match(match),
        let_op=match.limitations_nl or _DEFAULT_LET_OP,
        official_excerpts=[],
    )


def _obligations_from_match(match: LaypersonTopicMatch) -> list[ObligationRow]:
    if match.obligations_nl:
        return list(match.obligations_nl)
    summary = match.summary_nl.strip()
    if not summary:
        return []
    return [ObligationRow(label="Kernregel", uitleg=summary[:400])]


def _legal_basis_from_match(match: LaypersonTopicMatch) -> list[ArticleSummary]:
    if match.legal_basis_nl:
        return list(match.legal_basis_nl)
    if match.summary_nl.strip():
        return [ArticleSummary(
            article="—",
            title=match.regulation_title,
            uitleg_nl=match.summary_nl.strip()[:500],
        )]
    return []


def _terms_from_match(match: LaypersonTopicMatch) -> list[TermDefinition]:
    return list(match.terms_nl) if match.terms_nl else []
