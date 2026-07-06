"""Build rule-only interpretation plans for the declarant pipeline."""
from backend.src.services.llm_legal_planner_service import LlmLegalPlannerService
from backend.src.utils.hypothesis_plan_merge import merge_case_analysis_into_plan
from shared.schemas.declarant_dossier import DeclarantThinkResult
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan


class DeclarantPlanBuilderService:
    """Merge case analysis with rule planner — no LLM planner."""

    def __init__(self) -> None:
        self._planner = LlmLegalPlannerService()

    def build(
        self,
        think: DeclarantThinkResult,
    ) -> LegalInterpretationPlan:
        question = think.effective_question
        analysis = think.analysis
        base = self._planner.interpret_rule_only(question)
        instruments = self._apply_hypothesis_instruments(base, think)
        plan = base.model_copy(update={
            "instruments": instruments,
            "legal_actor": "unknown",
            "planner_source": "rule_fallback",
        })
        if analysis is None:
            return plan
        merged = merge_case_analysis_into_plan(plan, analysis)
        return merged.model_copy(update={
            "instruments": self._apply_hypothesis_instruments(merged, think) or merged.instruments,
            "legal_actor": "unknown",
            "planner_source": "rule_fallback",
            "reasoning_brief": analysis.case_summary[:200],
        })

    def _apply_hypothesis_instruments(
        self,
        plan: LegalInterpretationPlan,
        think: DeclarantThinkResult,
    ) -> list[InstrumentTarget]:
        if not think.hypothesis_celex:
            return plan.instruments
        built: list[InstrumentTarget] = []
        for celex in think.hypothesis_celex:
            articles = list(think.articles_by_celex.get(celex, ()))
            existing = next((i for i in plan.instruments if i.celex == celex), None)
            if existing:
                merged_articles = articles or list(existing.articles)
                built.append(existing.model_copy(update={"articles": merged_articles}))
            else:
                built.append(InstrumentTarget(
                    name=f"EU {celex}",
                    celex=celex,
                    articles=articles,
                    confidence=0.85,
                ))
        for inst in plan.instruments:
            if inst.celex and inst.celex not in {b.celex for b in built}:
                built.append(inst)
        return built[:3]
