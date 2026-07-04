"""Agent-path answer orchestration with gap-as-exception policy."""
from typing import Any

from backend.src.services.answer_bundle_assembly_service import AnswerBundleAssemblyService
from backend.src.services.citation_verifier_service import CitationVerifierService
from backend.src.services.coverage_guidance_service import CoverageGuidanceService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.services.citation_builder_service import CitationBuilderService
from backend.src.services.layperson_answer_service import LaypersonAnswerService
from backend.src.services.legal_extractive_generic import build_generic_layperson, can_build_generic_answer
from backend.src.services.llm_service import LlmService
from backend.src.services.question_intent_service import QuestionIntentService
from backend.src.services.source_consistency_service import SourceConsistencyService
from backend.src.utils.layperson_answer_formatter import is_hybrid_boilerplate, is_weak_layperson_answer
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


class AgentAnswerService:
    """Build answers from agent fetch results; gap only on real miss."""

    def __init__(self) -> None:
        self._llm = LlmService()
        self._verifier = CitationVerifierService()
        self._assembly = AnswerBundleAssemblyService()
        self._intent = QuestionIntentService()
        self._coverage = CoverageGuidanceService()
        self._source_consistency = SourceConsistencyService()
        self._layperson = LaypersonAnswerService()
        self._citations = CitationBuilderService()

    async def build(
        self,
        request: QueryRequest,
        fetch: AgentFetchResult,
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
    ) -> dict[str, Any]:
        route = "agent_flow"
        intent = self._intent.analyze(request.question)
        guidance = self._coverage.resolve(request.question)
        if plan.is_national_law:
            return self._assembly.insufficient_bundle(
                request, route, "topic_not_in_corpus", intent, guidance,
            )
        if fetch.chunks:
            return await self._answer_from_chunks(request, fetch.chunks, plan, history, route, guidance)
        if fetch.fetch_attempted:
            return self._fetch_attempted_gap(request, plan, fetch, route, intent, guidance)
        return self._assembly.insufficient_bundle(
            request, route, "no_chunks", intent, guidance,
        )

    async def _answer_from_chunks(
        self,
        request: QueryRequest,
        chunks: list[dict],
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
        route: str,
        guidance: Any,
    ) -> dict[str, Any]:
        if request.audience == "layperson" and can_build_generic_answer(chunks, request.question):
            prose = build_generic_layperson(request.question, chunks)
            if prose and not is_weak_layperson_answer(prose):
                citations = self._source_consistency.filter_citations(
                    self._citations.from_chunks(chunks), chunks,
                )
                adequacy = AdequacyResult(is_adequate=True, coverage_status="adequate")
                return self._assembly.finalize(
                    request, prose, citations, chunks, route, adequacy, guidance,
                )
        answer_text, citations = await self._llm.generate_answer(
            request.question, chunks, history, request.query_mode, request.audience,
            context_quality="hoog",
        )
        answer_text = self._improve_layperson_answer(request, chunks, answer_text)
        citations = self._source_consistency.filter_citations(citations, chunks)
        supported, verified_text, _issues = await self._verifier.verify(
            answer_text, chunks, plan,
        )
        if not supported:
            intent = self._intent.analyze(request.question)
            return self._fetch_attempted_gap(
                request, plan,
                AgentFetchResult(chunks=chunks, fetch_ok=True, fetch_attempted=True),
                route, intent, guidance,
                partial_answer=verified_text,
            )
        adequacy = AdequacyResult(is_adequate=True, coverage_status="adequate")
        return self._assembly.finalize(
            request, verified_text, citations, chunks, route, adequacy, guidance,
        )

    def _improve_layperson_answer(
        self,
        request: QueryRequest,
        chunks: list[dict],
        answer_text: str,
    ) -> str:
        if request.audience != "layperson":
            return answer_text
        if is_weak_layperson_answer(answer_text) or is_hybrid_boilerplate(answer_text):
            extractive = build_generic_layperson(request.question, chunks)
            if extractive and not is_weak_layperson_answer(extractive):
                return extractive.strip()
            if extractive:
                answer_text = extractive
        return self._layperson.format(answer_text, request.question, chunks)

    def _fetch_attempted_gap(
        self,
        request: QueryRequest,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        route: str,
        intent: Any,
        guidance: Any,
        partial_answer: str | None = None,
    ) -> dict[str, Any]:
        labels = [
            regulation_label(inst.celex, inst.title or inst.name)
            for inst in plan.instruments if inst.celex
        ]
        detail = ", ".join(labels) or ", ".join(fetch.attempted_celex)
        opener = (
            f"Ik heb {detail} geraadpleegd, maar kon op dit moment geen betrouwbare "
            "artikelteksten ophalen om uw vraag te beantwoorden."
        )
        answer_text = f"## Kort antwoord\n{opener}"
        if partial_answer:
            answer_text += f"\n\n## Gedeeltelijk antwoord\n{partial_answer}"
        answer_text += "\n\n## Wat u wél kunt doen\n- Zoek direct op [EUR-Lex](https://eur-lex.europa.eu/)."
        adequacy = AdequacyResult(
            is_adequate=False, reason="fetch_attempted", coverage_status="insufficient",
        )
        return self._assembly.finalize(
            request, answer_text, [], fetch.chunks, route, adequacy, guidance,
        )
