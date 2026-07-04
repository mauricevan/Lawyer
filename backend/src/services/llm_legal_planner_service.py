"""LLM-driven legal question interpretation (ADR-0009 fase 2)."""
import logging
import re

from backend.src.services.legal_question_classifier_service import classify_legal_question
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.legal_actor_issue_routing import apply_context_to_plan
from backend.src.utils.legal_domain_retrieval_filter import filter_instruments_by_domain
from backend.src.utils.legal_planner_prompt_context import build_planner_interpretation_hints
from backend.src.utils.legal_question_interpretation import infer_legal_context
from backend.src.services.question_intent_service import QuestionIntentService
from backend.src.utils.llm_json_client import call_llm_json
from ingestion.src.data.oj_citation_parser import parse_oj_celex
from shared.config.prompt_loader import get_legal_planner_system_prompt, get_legal_planner_user_template
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan

logger = logging.getLogger(__name__)
_CONFIDENCE_THRESHOLD = 0.5
_NATIONAL_PATTERNS = (
    "nederlandse wet", "nl wet", "nederlands recht", "vakantiedagen",
    "minimumloon", "belgisch recht", "gemeentelijke",
)


class LlmLegalPlannerService:
    """Interpret questions into EU instruments and article targets."""

    def __init__(self) -> None:
        self._intent = QuestionIntentService()
        self._rule_planner = LegalSourcePlannerService()

    async def interpret(
        self,
        question: str,
        history: list[dict] | None = None,
    ) -> LegalInterpretationPlan:
        if self._is_national_law_quick(question):
            return self._national_plan(question)
        try:
            plan = await self._llm_plan(question, history)
            if plan.confidence >= _CONFIDENCE_THRESHOLD and plan.instruments:
                return apply_context_to_plan(plan, question)
        except Exception as exc:
            logger.warning("LLM legal planner failed: %s", exc)
        return apply_context_to_plan(self._rule_fallback(question), question)

    async def _llm_plan(
        self,
        question: str,
        history: list[dict] | None,
    ) -> LegalInterpretationPlan:
        history_block = _format_history(history)
        hints = build_planner_interpretation_hints(question)
        user = get_legal_planner_user_template().format(
            question=question,
            history_block=history_block,
            interpretation_hints=hints,
        )
        raw = await call_llm_json(get_legal_planner_system_prompt(), user)
        plan = LegalInterpretationPlan.model_validate({**raw, "planner_source": "llm"})
        return _normalize_plan(plan, question)

    def _rule_fallback(self, question: str) -> LegalInterpretationPlan:
        intent = self._intent.analyze(question)
        instruments: list[InstrumentTarget] = []
        oj_celex = parse_oj_celex(question)
        if oj_celex:
            instruments.append(InstrumentTarget(
                name=_instrument_name_from_question(question),
                celex=oj_celex,
                articles=list(intent.article_refs),
                confidence=0.85,
            ))
        plan = self._rule_planner.plan(question)
        if plan and plan.celex:
            existing = next((i for i in instruments if i.celex == plan.celex), None)
            if existing:
                if plan.articles and not existing.articles:
                    idx = instruments.index(existing)
                    instruments[idx] = existing.model_copy(update={"articles": list(plan.articles)})
            elif not any(i.celex == plan.celex for i in instruments):
                instruments.append(InstrumentTarget(
                    name=plan.plan_id,
                    celex=plan.celex,
                    articles=list(plan.articles),
                    confidence=0.7,
                ))
        if not instruments and intent.suggested_celex:
            instruments.append(InstrumentTarget(
                name=intent.legal_domain or "EU-regelgeving",
                celex=intent.suggested_celex,
                articles=list(intent.article_refs),
                confidence=0.55,
            ))
        actor, issue = infer_legal_context(question)
        routing = classify_legal_question(question).legal_domain
        return LegalInterpretationPlan(
            question_type=_map_question_type(intent.question_type),
            legal_actor=actor,
            legal_issue=issue,
            legal_domain=routing,
            legal_question_type=classify_legal_question(question).legal_question_type,
            is_eu_law=not self._is_national_law_quick(question),
            is_national_law=self._is_national_law_quick(question),
            instruments=instruments,
            search_keywords=list(intent.eurlex_search_terms),
            confidence=0.65 if instruments else 0.3,
            reasoning_brief="Rule-based fallback planner",
            planner_source="rule_fallback",
        )

    def _national_plan(self, question: str) -> LegalInterpretationPlan:
        return LegalInterpretationPlan(
            question_type="scope",
            is_eu_law=False,
            is_national_law=True,
            instruments=[],
            search_keywords=[],
            confidence=0.9,
            reasoning_brief="National law scope detected",
            planner_source="rule_fallback",
        )

    def _is_national_law_quick(self, question: str) -> bool:
        lowered = question.lower()
        return any(p in lowered for p in _NATIONAL_PATTERNS)


def _format_history(history: list[dict] | None) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-4:]:
        role = msg.get("role", "user")
        content = str(msg.get("content", ""))[:300]
        lines.append(f"{role}: {content}")
    return "Recente context:\n" + "\n".join(lines)


def _instrument_name_from_question(question: str) -> str:
    match = re.search(
        r"(?i)(reach|avg|gdpr|ai act|ucc|douanewetboek|milieuaansprakelijkheid)[-\s\w]*",
        question,
    )
    if match:
        return match.group(1)
    return "EU-regelgeving"


def _map_question_type(intent_type: str) -> str:
    mapping = {
        "article_lookup": "scope",
        "comparison": "comparison",
        "procedure": "procedure",
        "definition": "definition",
    }
    return mapping.get(intent_type, "obligation")


def _normalize_plan(plan: LegalInterpretationPlan, question: str) -> LegalInterpretationPlan:
    classification = classify_legal_question(question)
    actor = plan.legal_actor if plan.legal_actor != "unknown" else classification.legal_actor
    domain = plan.legal_domain if plan.legal_domain != "unknown" else classification.legal_domain
    question_type = (
        plan.legal_question_type
        if plan.legal_question_type != "unknown"
        else classification.legal_question_type
    )
    instruments = filter_instruments_by_domain(plan.instruments[:3], domain)
    keywords = [k.lower().strip() for k in plan.search_keywords if k.strip()][:8]
    return plan.model_copy(update={
        "instruments": instruments,
        "search_keywords": keywords,
        "legal_actor": actor,
        "legal_domain": domain,
        "legal_question_type": question_type,
    })
