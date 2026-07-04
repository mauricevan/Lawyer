"""V8.1 structured judgment builder — seven mandatory sections."""
from backend.src.utils.effect_law_mapping import map_effect_to_law
from backend.src.utils.proportionality_engine import ProportionalityAssessment, assess_proportionality
from shared.schemas.case_law_simulation import (
    LegalEffectClassification,
    ProportionalitySteps,
    StructuredJudgment,
)
from shared.schemas.legal_conflict import LegalCaseAnalysis, PrimaryLegalConflict
from shared.schemas.legal_effect import LegalEffectType

_ISSUE_TEMPLATES: dict[tuple[PrimaryLegalConflict, LegalEffectType | None], str] = {
    ("internal_market_restriction", "discrimination_by_establishment"): (
        "Whether a Member State requirement limiting online platforms to EU-established "
        "advertisers constitutes a restriction on the freedom to provide services under "
        "Article 56 TFEU and Directive 2000/31/EC."
    ),
    ("internal_market_restriction", "licensing_or_authorisation"): (
        "Whether a Member State measure imposing prior authorisation for online service "
        "providers is compatible with Article 56 TFEU and Directive 2000/31/EC."
    ),
    ("internal_market_restriction", None): (
        "Whether a Member State measure restricting cross-border online services is "
        "compatible with Article 56 TFEU and Directive 2000/31/EC."
    ),
}


class StructuredJudgmentBuilder:
    """Build fixed arrest-logic judgment from case analysis."""

    def build(
        self,
        analysis: LegalCaseAnalysis,
        proportionality: ProportionalityAssessment | None = None,
    ) -> StructuredJudgment:
        """Produce all seven mandatory sections."""
        prop = proportionality or assess_proportionality(analysis)
        issue = self._build_issue(analysis)
        laws = self._applicable_law(analysis)
        restriction = self._restriction_analysis(analysis)
        aim = self._legitimate_aim(analysis)
        conclusion = self._court_conclusion(analysis, prop)
        effect = self._legal_effect_classification(analysis, prop)
        return StructuredJudgment(
            issue=issue,
            applicable_eu_law=laws,
            restriction_analysis=restriction,
            legitimate_aim=aim,
            proportionality=ProportionalitySteps(
                suitability=prop.suitability_text,
                necessity=prop.necessity_text,
                balancing=prop.balancing_text,
                is_complete=prop.is_complete,
            ),
            court_conclusion=conclusion,
            legal_effect_classification=effect,
        )

    def _build_issue(self, analysis: LegalCaseAnalysis) -> str:
        effect_type = analysis.legal_effect.legal_effect_type if analysis.legal_effect else None
        key = (analysis.primary_legal_conflict, effect_type)
        if key in _ISSUE_TEMPLATES:
            return _ISSUE_TEMPLATES[key]
        fallback = _ISSUE_TEMPLATES.get((analysis.primary_legal_conflict, None))
        if fallback:
            return fallback
        return (
            "Whether the national measure at issue is compatible with the applicable "
            "provisions of EU law governing the internal market."
        )

    def _applicable_law(self, analysis: LegalCaseAnalysis) -> list[str]:
        laws = ["Article 56 TFEU (freedom to provide services)"]
        if analysis.legal_effect:
            mapping = map_effect_to_law(analysis.legal_effect, analysis.primary_legal_conflict)
            for framework in mapping.frameworks[:2]:
                if "2000/31" in framework or "information society" in framework.lower():
                    laws.append("Directive 2000/31/EC (country of origin principle, restriction limits)")
                    break
        if len(laws) == 1 and analysis.default_celex == "32000L0031":
            laws.append("Directive 2000/31/EC (country of origin principle, restriction limits)")
        return laws[:6]

    def _restriction_analysis(self, analysis: LegalCaseAnalysis) -> str:
        effect = analysis.legal_effect
        if effect and effect.legal_effect_type == "discrimination_by_establishment":
            return (
                "The measure constitutes a restriction because it discriminates against "
                "non-EU-established service providers and limits cross-border online services."
            )
        if effect and effect.legal_effect_type == "licensing_or_authorisation":
            return (
                "The measure constitutes a restriction because it introduces a prior "
                "authorisation requirement for cross-border online services."
            )
        return (
            "The measure constitutes a restriction because it limits cross-border "
            "provision of online services within the internal market."
        )

    def _legitimate_aim(self, analysis: LegalCaseAnalysis) -> str:
        if not analysis.legal_effect:
            return "Public policy objectives as invoked by the Member State."
        aims = {
            "discrimination_by_establishment": "Consumer protection and fraud prevention.",
            "licensing_or_authorisation": "Consumer protection and online safety.",
            "market_access_prohibition": "Public order and health protection.",
            "additional_requirement": "Consumer protection and legal certainty.",
            "enforcement_measure": "Effective enforcement and market surveillance.",
            "procedural_burden": "Transparency and legal certainty.",
        }
        return aims.get(analysis.legal_effect.legal_effect_type, "Consumer protection.")

    def _court_conclusion(self, analysis: LegalCaseAnalysis, prop: ProportionalityAssessment) -> str:
        if not self._has_restriction(analysis):
            return "The measure does not constitute a restriction incompatible with EU law."
        if prop.passes_overall:
            return (
                "The measure constitutes a justified and proportionate restriction "
                "compatible with Article 56 TFEU."
            )
        return (
            "The measure constitutes a disproportionate restriction incompatible "
            "with Article 56 TFEU."
        )

    def _legal_effect_classification(
        self,
        analysis: LegalCaseAnalysis,
        prop: ProportionalityAssessment,
    ) -> LegalEffectClassification:
        if not self._has_restriction(analysis):
            return "no restriction under EU law"
        if prop.passes_overall:
            return "justified and proportionate restriction"
        if prop.is_suitable and analysis.legal_effect:
            return "justified but disproportionate restriction"
        hint = analysis.legal_effect.effect_conclusion_hint if analysis.legal_effect else None
        if hint == "prohibited" or not prop.passes_overall:
            return "prohibited restriction"
        return "justified but disproportionate restriction"

    def _has_restriction(self, analysis: LegalCaseAnalysis) -> bool:
        if analysis.primary_legal_conflict == "platform_governance_issue":
            return False
        return True
