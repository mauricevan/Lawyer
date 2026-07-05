"""Agent-path answer orchestration with gap-as-exception policy."""
from typing import Any

from backend.src.config import settings
from backend.src.services.answer_bundle_assembly_service import AnswerBundleAssemblyService
from backend.src.services.citation_verifier_service import CitationVerifierService
from backend.src.services.coverage_guidance_service import CoverageGuidanceService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.services.citation_builder_service import CitationBuilderService
from backend.src.services.layperson_answer_service import LaypersonAnswerService
from backend.src.services.layperson_clear_answer_composer import LaypersonClearAnswerComposer
from backend.src.services.layperson_conversation_service import LaypersonConversationService
from backend.src.services.legal_extractive_generic import can_build_generic_answer
from backend.src.services.llm_service import LlmService
from backend.src.services.question_intent_service import QuestionIntentService
from backend.src.services.source_consistency_service import SourceConsistencyService
from backend.src.utils.layperson_domain_gate import is_wrong_domain_answer
from backend.src.utils.legal_domain_retrieval_filter import (
    filter_chunks_by_domain,
    rank_chunks_by_domain,
)
from backend.src.utils.legal_question_type_chunk_scoring import (
    filter_chunks_for_question_type_retry,
    rank_chunks_by_question_type,
)
from backend.src.utils.layperson_answer_formatter import is_hybrid_boilerplate, is_weak_layperson_answer
from backend.src.utils.layperson_gap_policy import is_publishable_clear_answer
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.evidence_validation import EvidenceFailureReason, EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


_REASON_LABELS: dict[EvidenceFailureReason, str] = {
    "no_chunks": "geen bronteksten gevonden",
    "procedural_only": "alleen procedurele teksten (geen inhoudelijke artikelen)",
    "domain_mismatch": "bronnen passen niet bij het rechtsgebied",
    "actor_mismatch": "bronnen sluiten niet aan op de juridische actor in de vraag",
    "subject_mismatch": "bronnen beantwoorden het onderwerp van de vraag niet",
    "insufficient_substance": "onvoldoende inhoudelijke juridische onderbouwing",
    "effect_mismatch": "bronnen ondersteunen het juridische effect niet",
}


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
        self._clear_composer = LaypersonClearAnswerComposer()
        self._conversation = LaypersonConversationService()

    async def build(
        self,
        request: QueryRequest,
        fetch: AgentFetchResult,
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
        evidence: EvidenceValidationResult | None = None,
        reconciliation: ReconciliationResult | None = None,
        analysis: LegalCaseAnalysis | None = None,
    ) -> dict[str, Any]:
        route = "agent_flow"
        intent = self._intent.analyze(request.question)
        guidance = self._coverage.resolve(request.question)
        if plan.is_national_law:
            return self._assembly.insufficient_bundle(
                request, route, "topic_not_in_corpus", intent, guidance,
            )
        if reconciliation and reconciliation.conclusion == "contradicted":
            return self._insufficient_reconciliation_gap(
                request, plan, fetch, route, intent, guidance, reconciliation, evidence,
            )
        if evidence and not evidence.is_valid:
            return self._insufficient_evidence_gap(request, plan, fetch, route, intent, guidance, evidence)
        if fetch.chunks:
            return await self._answer_from_chunks(
                request, fetch.chunks, plan, history, route, guidance, analysis,
            )
        if fetch.fetch_attempted:
            clear = await self._resolve_clear_fallback(request, fetch.chunks, plan)
            if clear:
                return self._finalize_clear_answer(request, clear, fetch.chunks, route, guidance)
            return self._fetch_attempted_gap(request, plan, fetch, route, intent, guidance)
        return self._assembly.insufficient_bundle(
            request, route, "no_chunks", intent, guidance,
        )

    async def build_no_domain_gap(self, request: QueryRequest) -> dict[str, Any]:
        """V4 hard-fail when no legal domain could be mapped from the conflict."""
        route = "agent_flow"
        intent = self._intent.analyze(request.question)
        guidance = self._coverage.resolve(request.question)
        answer_text = (
            "## Kort antwoord\n"
            "Er kon geen primair juridisch conflict en rechtsgebied worden bepaald. "
            "Zonder dat kan het systeem geen betrouwbare EU-bronnen opzoeken.\n\n"
            "## Wat u wél kunt doen\n"
            "- Formuleer de vraag met meer context (wie doet wat, in welke situatie).\n"
            "- Raadpleeg [EUR-Lex](https://eur-lex.europa.eu/) of een gekwalificeerd jurist."
        )
        adequacy = AdequacyResult(
            is_adequate=False, reason="no_domain", coverage_status="insufficient",
        )
        return self._assembly.finalize(
            request, answer_text, [], [], route, adequacy, guidance,
        )

    async def _answer_from_chunks(
        self,
        request: QueryRequest,
        chunks: list[dict],
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
        route: str,
        guidance: Any,
        analysis: LegalCaseAnalysis | None = None,
    ) -> dict[str, Any]:
        if request.audience == "layperson" and can_build_generic_answer(chunks, request.question):
            prose = await self._compose_layperson_answer(request, chunks, plan)
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
        answer_text = await self._improve_layperson_answer(request, chunks, answer_text)
        citations = self._source_consistency.filter_citations(citations, chunks)
        supported, verified_text, _issues = await self._verifier.verify(
            answer_text, chunks, plan,
        )
        if not supported:
            intent = self._intent.analyze(request.question)
            clear = await self._resolve_clear_fallback(request, chunks, plan)
            if clear:
                return self._finalize_clear_answer(request, clear, chunks, route, guidance)
            if is_publishable_clear_answer(verified_text):
                return self._finalize_clear_answer(request, verified_text.strip(), chunks, route, guidance)
            return self._fetch_attempted_gap(
                request, plan,
                AgentFetchResult(chunks=chunks, fetch_ok=True, fetch_attempted=True),
                route, intent, guidance,
                partial_answer=verified_text if verified_text.strip() else None,
            )
        adequacy = AdequacyResult(is_adequate=True, coverage_status="adequate")
        return self._assembly.finalize(
            request, verified_text, citations, chunks, route, adequacy, guidance,
        )

    async def _improve_layperson_answer(
        self,
        request: QueryRequest,
        chunks: list[dict],
        answer_text: str,
    ) -> str:
        if request.audience != "layperson":
            return answer_text
        if settings.layperson_conversation_llm_enabled and chunks:
            conversational = await self._conversation.compose_answer(
                request.question, chunks, answer_text,
            )
            if conversational:
                return conversational.strip()
        if is_weak_layperson_answer(answer_text) or is_hybrid_boilerplate(answer_text):
            extractive = self._clear_composer.compose_without_llm(
                request.question, chunks, allow_topic=False,
            )
            if not extractive or is_weak_layperson_answer(extractive):
                extractive = await self._clear_composer.compose(request.question, chunks)
            if extractive and not is_weak_layperson_answer(extractive):
                return extractive.strip()
            if extractive:
                answer_text = extractive
        return self._layperson.format(answer_text, request.question, chunks)

    async def _compose_layperson_answer(
        self,
        request: QueryRequest,
        chunks: list[dict],
        plan: LegalInterpretationPlan,
    ) -> str | None:
        prose = await self._clear_composer.compose(request.question, chunks)
        if not prose:
            return None
        if not self._needs_domain_retry(prose, plan, chunks):
            return prose
        filtered = rank_chunks_by_question_type(
            rank_chunks_by_domain(
                filter_chunks_for_question_type_retry(
                    filter_chunks_by_domain(chunks, plan.legal_domain),
                    plan.legal_question_type,
                ),
                plan.legal_domain,
            ),
            plan.legal_question_type,
        )
        retry = self._clear_composer.compose_without_llm(
            request.question, filtered, allow_topic=False,
        )
        if retry and not self._needs_domain_retry(retry, plan, filtered):
            return retry
        retry_async = await self._clear_composer.compose(request.question, filtered)
        if retry_async and not self._needs_domain_retry(retry_async, plan, filtered):
            return retry_async
        return retry or prose

    def _needs_domain_retry(
        self,
        prose: str,
        plan: LegalInterpretationPlan,
        chunks: list[dict],
    ) -> bool:
        celexes = [str(chunk.get("celex", "")) for chunk in chunks if chunk.get("celex")]
        return is_wrong_domain_answer(
            prose,
            plan.legal_actor,
            plan.legal_domain,
            celexes,
            plan.legal_question_type,
        )

    async def _resolve_clear_fallback(
        self,
        request: QueryRequest,
        chunks: list[dict],
        plan: LegalInterpretationPlan,
    ) -> str | None:
        if request.audience != "layperson":
            return None
        prose = self._clear_composer.compose_without_llm(
            request.question, chunks, allow_topic=False,
        )
        if prose and is_publishable_clear_answer(prose) and not self._needs_domain_retry(prose, plan, chunks):
            return prose.strip()
        prose = await self._clear_composer.compose(request.question, chunks)
        if prose and is_publishable_clear_answer(prose) and not self._needs_domain_retry(prose, plan, chunks):
            return prose.strip()
        return None

    def _finalize_clear_answer(
        self,
        request: QueryRequest,
        answer_text: str,
        chunks: list[dict],
        route: str,
        guidance: Any,
    ) -> dict[str, Any]:
        citations = self._source_consistency.filter_citations(
            self._citations.from_chunks(chunks), chunks,
        )
        adequacy = AdequacyResult(is_adequate=True, coverage_status="adequate")
        return self._assembly.finalize(
            request, answer_text, citations, chunks, route, adequacy, guidance,
        )

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
        if partial_answer and is_publishable_clear_answer(partial_answer):
            return self._finalize_clear_answer(
                request, partial_answer.strip(), fetch.chunks, route, guidance,
            )
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

    def _insufficient_evidence_gap(
        self,
        request: QueryRequest,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        route: str,
        intent: Any,
        guidance: Any,
        evidence: EvidenceValidationResult,
    ) -> dict[str, Any]:
        if request.audience == "layperson":
            adequacy = AdequacyResult(
                is_adequate=False,
                reason="insufficient_evidence",
                coverage_status="insufficient",
            )
            return self._assembly.gap_bundle(
                request, fetch.chunks, route, adequacy, guidance, intent,
            )
        labels = [
            regulation_label(inst.celex, inst.title or inst.name)
            for inst in plan.instruments if inst.celex
        ]
        detail = ", ".join(labels) or ", ".join(fetch.attempted_celex)
        reason_text = "; ".join(
            _REASON_LABELS.get(reason, reason) for reason in evidence.reasons
        )
        opener = (
            "Er zijn onvoldoende betrouwbare EUR-Lex-bronnen gevonden om deze juridische "
            "vraag te onderbouwen."
        )
        if reason_text:
            opener += f" Reden: {reason_text}."
        if detail:
            opener = (
                f"Ik heb {detail} geraadpleegd. {opener}"
            )
        answer_text = (
            f"## Kort antwoord\n{opener}\n\n"
            "## Wat u wél kunt doen\n"
            "- Zoek de actuele tekst op [EUR-Lex](https://eur-lex.europa.eu/).\n"
            "- Raadpleeg een gekwalificeerd jurist voor uw concrete situatie."
        )
        adequacy = AdequacyResult(
            is_adequate=False, reason="insufficient_evidence", coverage_status="insufficient",
        )
        return self._assembly.finalize(
            request, answer_text, [], fetch.chunks, route, adequacy, guidance,
        )

    def _insufficient_reconciliation_gap(
        self,
        request: QueryRequest,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        route: str,
        intent: Any,
        guidance: Any,
        reconciliation: ReconciliationResult,
        evidence: EvidenceValidationResult | None,
    ) -> dict[str, Any]:
        if evidence and not evidence.is_valid:
            return self._insufficient_evidence_gap(
                request, plan, fetch, route, intent, guidance, evidence,
            )
        opener = (
            "De gevonden EU-bronnen ondersteunen de juridische analyse onvoldoende om "
            "een betrouwbaar antwoord te geven."
        )
        if reconciliation.rationale:
            opener += f" {reconciliation.rationale}"
        answer_text = (
            f"## Kort antwoord\n{opener}\n\n"
            "## Wat u wél kunt doen\n"
            "- Zoek de actuele tekst op [EUR-Lex](https://eur-lex.europa.eu/).\n"
            "- Raadpleeg een gekwalificeerd jurist voor uw concrete situatie."
        )
        adequacy = AdequacyResult(
            is_adequate=False, reason="reconciliation_failed", coverage_status="insufficient",
        )
        return self._assembly.finalize(
            request, answer_text, [], fetch.chunks, route, adequacy, guidance,
        )
