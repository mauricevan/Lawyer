"""V4 legal case analysis: hypothesis + primary conflict + domain mapping."""
from backend.src.services.legal_hypothesis_service import LegalHypothesisService
from backend.src.services.primary_legal_conflict_service import (
    infer_context,
    infer_parties,
    select_primary_legal_conflict,
)
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_hypothesis import LegalHypothesis


class LegalCaseAnalysisService:
    """Build V4 case analysis before any EUR-Lex retrieval."""

    def __init__(self) -> None:
        self._hypothesis = LegalHypothesisService()

    async def analyze(
        self,
        question: str,
        history: list[dict] | None = None,
    ) -> LegalCaseAnalysis:
        """Form hypothesis, select primary conflict, map domain deterministically."""
        hypothesis = await self._hypothesis.form(question, history)
        conflict = select_primary_legal_conflict(question, hypothesis)
        mapping = map_conflict_to_domain(conflict)
        parties = infer_parties(question) or _parties_from_actor(hypothesis.legal_actor)
        return LegalCaseAnalysis(
            case_summary=hypothesis.legal_problem,
            parties=parties,
            context=infer_context(question),
            possible_domains=_possible_domains(mapping.domain),
            primary_legal_conflict=conflict,
            legal_domain=mapping.domain,
            legal_actor=hypothesis.legal_actor,
            legal_question_type=hypothesis.legal_question_type,
            likely_eu_frameworks=list(mapping.frameworks),
            default_celex=mapping.default_celex,
        )

    def to_hypothesis(self, analysis: LegalCaseAnalysis) -> LegalHypothesis:
        """Expose V4 analysis through the existing LegalHypothesis API shape."""
        return LegalHypothesis(
            legal_problem=analysis.case_summary,
            legal_actor=analysis.legal_actor,
            legal_domain_guess=analysis.legal_domain,
            likely_eu_frameworks=analysis.likely_eu_frameworks,
            legal_question_type=analysis.legal_question_type,
            case_summary=analysis.case_summary,
            parties=analysis.parties,
            context=analysis.context,
            possible_domains=list(analysis.possible_domains),
            primary_legal_conflict=analysis.primary_legal_conflict,
            source="rule",
        )


def _parties_from_actor(actor: str) -> list[str]:
    if actor == "unknown":
        return []
    return [actor]


def _possible_domains(primary: str) -> list[str]:
    secondary = {
        "internal_market": ["consumer_protection"],
        "consumer_protection": ["internal_market"],
        "employment_law": ["data_protection"],
    }
    return [primary, *secondary.get(primary, [])][:4]
