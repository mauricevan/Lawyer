"""Declarant THINK step — reason before any EUR-Lex retrieval."""
from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService
from backend.src.services.legal_case_analysis_service import LegalCaseAnalysisService
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.clarification_history_merge import clarification_turn_count
from backend.src.utils.effective_question_resolver import resolve_effective_question
from shared.schemas.declarant_dossier import DeclarantPhase, DeclarantThinkResult
from shared.schemas.query import QueryRequest

_MAX_CLARIFICATION_ROUNDS = 2
_VWEU_CELEX_PREFIX = "12016"


class DeclarantThinkService:
    """Decide if the question is ready for targeted EUR-Lex fetch."""

    def __init__(self) -> None:
        self._case = LegalCaseAnalysisService()
        self._ambiguity = LegalAmbiguityDetectorService()
        self._ilcl = LegalClarificationOrchestrator()
        self._planner = LegalSourcePlannerService()

    async def think(
        self,
        request: QueryRequest,
        history: list[dict] | None,
    ) -> DeclarantThinkResult:
        effective = resolve_effective_question(request.question, history)
        analysis = await self._case.analyze(request.question, history)
        state, _score, reasons = self._ambiguity.detect(effective)
        rounds = clarification_turn_count(history)
        if state == "unanswerable":
            return self._gap(effective, analysis, "buiten EU-rechtsgebied")
        ilcl = self._ilcl.clarify(effective, history, request.audience)
        force_search = rounds >= _MAX_CLARIFICATION_ROUNDS
        if not force_search and not ilcl.should_proceed:
            return DeclarantThinkResult(
                phase=DeclarantPhase.CLARIFY,
                ready_to_search=False,
                effective_question=effective,
                user_goal=analysis.case_summary,
                analysis=analysis,
                ilcl_result=ilcl,
            )
        enriched = ilcl.enriched_question or effective
        celexes, articles_map = self._hypothesis_targets(enriched, analysis)
        if not celexes and state == "ambiguous" and not force_search:
            return DeclarantThinkResult(
                phase=DeclarantPhase.CLARIFY,
                ready_to_search=False,
                effective_question=effective,
                user_goal=analysis.case_summary,
                analysis=analysis,
                ilcl_result=ilcl,
            )
        return DeclarantThinkResult(
            phase=DeclarantPhase.FETCH,
            ready_to_search=True,
            effective_question=enriched,
            user_goal=analysis.case_summary,
            analysis=analysis,
            hypothesis_celex=celexes,
            articles_by_celex=articles_map,
            ilcl_result=ilcl if ilcl.mode == "assumption" else None,
        )

    def _hypothesis_targets(
        self,
        question: str,
        analysis,
    ) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
        source = self._planner.plan(question)
        celexes: list[str] = []
        articles: dict[str, tuple[str, ...]] = {}
        if source and source.celex:
            celexes.append(source.celex)
            if source.articles:
                articles[source.celex] = tuple(source.articles)
            for related in source.related_celex:
                celexes.append(related)
                if related.startswith(_VWEU_CELEX_PREFIX):
                    articles[related] = ("28",)
        elif analysis.default_celex:
            celexes.append(analysis.default_celex)
        return tuple(dict.fromkeys(celexes)), articles

    def _gap(self, effective: str, analysis, reason: str) -> DeclarantThinkResult:
        return DeclarantThinkResult(
            phase=DeclarantPhase.GAP,
            ready_to_search=False,
            effective_question=effective,
            user_goal=analysis.case_summary,
            analysis=analysis,
            gap_reason=reason,
        )
