"""V10.3 ILCL orchestrator — pre-retrieval legal clarification."""
from backend.src.services.clarification_assumption_service import ClarificationAssumptionService
from backend.src.services.clarification_question_service import ClarificationQuestionService
from backend.src.services.clarification_scenario_service import ClarificationScenarioService
from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService
from backend.src.utils.clarification_formatter import format_clarification_section
from backend.src.utils.effective_question_resolver import resolve_effective_question
from backend.src.utils.clarification_history_merge import (
    clarification_turn_count,
    is_scenario_selection,
    merge_clarification_history,
    prior_clarification_turn,
    user_refused_clarification,
    user_still_unsure,
)
from backend.src.utils.question_typo_normalizer import normalize_question_typos
from shared.schemas.legal_clarification import ClarificationMode, LegalClarificationResult


class LegalClarificationOrchestrator:
    """Convert ambiguous questions into a decidable legal case."""

    def __init__(self) -> None:
        self._detector = LegalAmbiguityDetectorService()
        self._questions = ClarificationQuestionService()
        self._scenarios = ClarificationScenarioService()
        self._assumption = ClarificationAssumptionService()

    def clarify(
        self,
        question: str,
        history: list[dict] | None = None,
        audience: str = "layperson",
    ) -> LegalClarificationResult:
        """Run ILCL decision tree without EUR-Lex retrieval."""
        question = normalize_question_typos(question)
        merged = resolve_effective_question(question, history)
        if prior_clarification_turn(history) and is_scenario_selection(question):
            state, score, reasons = self._detector.detect(merged)
            return self._build_mode_result(
                "assumption", merged, question, history, audience, score, reasons,
            )
        state, score, reasons = self._detector.detect(merged)
        if state == "clear":
            return self._result("clear", "skip", merged, score, reasons, audience=audience, should_proceed=True)
        if state == "unanswerable":
            return self._unanswerable(score, reasons)
        mode = self._pick_mode(merged, question, history, score, reasons)
        return self._build_mode_result(mode, merged, question, history, audience, score, reasons)

    def _pick_mode(
        self,
        merged: str,
        question: str,
        history: list[dict] | None,
        score: float,
        reasons: list[str],
    ) -> ClarificationMode:
        if user_refused_clarification(question) or is_scenario_selection(question):
            return "assumption"
        if prior_clarification_turn(history) or clarification_turn_count(history) >= 1:
            if user_still_unsure(question):
                return "scenarios"
            return "assumption"
        if score < 0.7 and self._detector.has_activity_detail(merged):
            return "assumption"
        return "questions"

    def _build_mode_result(
        self,
        mode: ClarificationMode,
        merged: str,
        question: str,
        history: list[dict] | None,
        audience: str,
        score: float,
        reasons: list[str],
    ) -> LegalClarificationResult:
        if mode == "assumption":
            narrative, enriched = self._assumption.build(merged, audience, question)
            return self._result(
                "ambiguous", "assumption", enriched, score, reasons,
                audience=audience, assumption_text=narrative, should_proceed=True,
            )
        if mode == "scenarios":
            scenarios = self._scenarios.suggest(merged, audience)
            return self._result(
                "ambiguous", "scenarios", merged, score, reasons,
                audience=audience, scenarios=scenarios, should_proceed=False,
            )
        questions = self._questions.build(reasons, audience, merged)
        return self._result(
            "ambiguous", "questions", merged, score, reasons,
            audience=audience, questions=questions, should_proceed=False,
        )

    def _unanswerable(self, score: float, reasons: list[str]) -> LegalClarificationResult:
        text = (
            "## Kort antwoord\n"
            "Deze vraag valt buiten het EU-rechtsgebied dat dit systeem behandelt.\n\n"
            "## Let op\n"
            "Stel uw vraag in EU-context (verordeningen, richtlijnen, Hof van Justitie)."
        )
        return LegalClarificationResult(
            state="unanswerable",
            mode="questions",
            ambiguity_score=score,
            ambiguity_reasons=reasons,
            enriched_question="",
            formatted_section=text,
            should_proceed=False,
        )

    def _result(
        self,
        state: str,
        mode: ClarificationMode,
        enriched_question: str,
        score: float,
        reasons: list[str],
        *,
        audience: str = "layperson",
        questions=None,
        scenarios=None,
        assumption_text: str = "",
        should_proceed: bool = True,
    ) -> LegalClarificationResult:
        result = LegalClarificationResult(
            state=state,  # type: ignore[arg-type]
            mode=mode,
            ambiguity_score=round(score, 3),
            ambiguity_reasons=reasons,
            questions=questions or [],
            scenarios=scenarios or [],
            assumption_text=assumption_text,
            enriched_question=enriched_question,
            should_proceed=should_proceed,
        )
        section = (
            format_clarification_section(result, audience)
            if mode != "skip"
            else ""
        )
        return result.model_copy(update={"formatted_section": section})
