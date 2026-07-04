"""V8.1 court simulation — structured CJEU arrest assessment."""
from backend.src.utils.proportionality_engine import assess_proportionality
from backend.src.utils.structured_judgment_builder import StructuredJudgmentBuilder
from backend.src.utils.structured_judgment_formatter import (
    format_structured_judgment,
    validate_structured_judgment_text,
)
from shared.schemas.case_law_simulation import (
    AlignmentWithAnswer,
    CaseLawSimulationResult,
    CourtFinalConclusion,
    CourtSimulationResult,
    StructureEnforcement,
)
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_effect import LegalEffectType

_JUSTIFICATION_MAP: dict[LegalEffectType, tuple[str, ...]] = {
    "discrimination_by_establishment": ("consumer protection", "fraud prevention", "public policy"),
    "market_access_prohibition": ("public order", "health protection"),
    "additional_requirement": ("consumer protection", "legal certainty"),
    "licensing_or_authorisation": ("public security", "consumer protection"),
    "procedural_burden": ("transparency", "legal certainty"),
    "enforcement_measure": ("effective enforcement", "market surveillance"),
}


class CourtSimulationService:
    """Simulate how the CJEU would assess the hypothetical case."""

    def __init__(self) -> None:
        self._builder = StructuredJudgmentBuilder()

    def simulate(
        self,
        analysis: LegalCaseAnalysis,
        final_answer: str,
        used_articles: list[str],
    ) -> CaseLawSimulationResult:
        """Run structured arrest simulation and compare with the draft answer."""
        proportionality = assess_proportionality(analysis)
        judgment = self._builder.build(analysis, proportionality)
        formatted = format_structured_judgment(judgment)
        structure_valid = validate_structured_judgment_text(formatted, judgment)
        enforcement = self._structure_enforcement(judgment, structure_valid)
        restriction = self._restriction_test(analysis)
        conclusion = self._final_conclusion(restriction["has_restriction"], proportionality.passes_overall)
        alignment = self._align_with_answer(judgment, analysis, final_answer)
        return CaseLawSimulationResult(
            hypothetical_case_title="Commission v Member State X (hypothetical)",
            issue_statement=judgment.issue,
            has_eu_restriction=restriction["has_restriction"],
            restriction_types=restriction["types"],
            possible_justifications=self._justification_test(analysis),
            proportionality_assessment=proportionality.summary,
            court_final_conclusion=conclusion,
            court_simulation_result=self._map_court_result(conclusion),
            reasoning_summary=judgment.court_conclusion,
            alignment_with_answer=alignment,
            structured_judgment=judgment,
            formatted_judgment=formatted,
            structure_valid=structure_valid,
            structure_enforcement=enforcement,
        )

    def _structure_enforcement(self, judgment, structure_valid: bool) -> StructureEnforcement:
        if not structure_valid:
            return "regenerate"
        if not judgment.proportionality.is_complete:
            return "fail"
        if not judgment.legal_effect_classification:
            return "fail"
        return "pass"

    def _restriction_test(self, analysis: LegalCaseAnalysis) -> dict:
        conflict = analysis.primary_legal_conflict
        types: list[str] = []
        if conflict in {"internal_market_restriction", "consumer_transaction_issue"}:
            types.extend(["freedom to provide services", "internal market"])
        if analysis.legal_effect and analysis.legal_effect.legal_effect_type == "discrimination_by_establishment":
            types.append("freedom of establishment")
        has = bool(types) or conflict != "platform_governance_issue"
        return {"has_restriction": has, "types": types[:4]}

    def _justification_test(self, analysis: LegalCaseAnalysis) -> list[str]:
        if not analysis.legal_effect:
            return ["proportionality"]
        return list(_JUSTIFICATION_MAP.get(analysis.legal_effect.legal_effect_type, ("proportionality",)))[:5]

    def _final_conclusion(self, has_restriction: bool, proportionality_passes: bool) -> CourtFinalConclusion:
        if not has_restriction:
            return "permitted"
        if proportionality_passes:
            return "permitted_under_conditions"
        return "prohibited"

    def _map_court_result(self, conclusion: CourtFinalConclusion) -> CourtSimulationResult:
        mapping: dict[CourtFinalConclusion, CourtSimulationResult] = {
            "permitted": "compatible_with_eu_law",
            "permitted_under_conditions": "compatible_under_conditions",
            "prohibited": "incompatible_with_eu_law",
        }
        return mapping[conclusion]

    def _align_with_answer(
        self,
        judgment,
        analysis: LegalCaseAnalysis,
        answer: str,
    ) -> AlignmentWithAnswer:
        answer_lower = answer.lower()
        effect = judgment.legal_effect_classification
        court_prohibits = effect in {"prohibited restriction", "justified but disproportionate restriction"}
        answer_prohibits = any(
            phrase in answer_lower
            for phrase in ("niet toegestaan", "mag niet", "in strijd", "verboden", "incompatible")
        )
        answer_permits = "**ja" in answer_lower or "mag wel" in answer_lower
        if effect == "prohibited restriction" and answer_prohibits:
            return "consistent"
        if effect == "justified and proportionate restriction" and "onder voorwaarden" in answer_lower:
            return "consistent"
        if court_prohibits and answer_permits:
            return "inconsistent"
        if court_prohibits and answer_prohibits:
            return "consistent"
        if court_prohibits and not answer_prohibits:
            return "inconsistent"
        return "partially_consistent"
