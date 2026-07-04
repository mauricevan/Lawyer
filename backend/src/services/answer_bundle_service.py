"""Build RAG answer bundles with layperson formatting and topic fallbacks."""
from typing import Any

from backend.src.services.answer_extractive_bundle_service import AnswerExtractiveBundleService
from backend.src.services.answer_bundle_assembly_service import AnswerBundleAssemblyService
from backend.src.services.answer_specificity_guard_service import AnswerSpecificityGuardService
from backend.src.services.answer_template_bundle_service import AnswerTemplateBundleService
from backend.src.services.context_adequacy_service import ContextAdequacyService
from backend.src.services.context_quality_service import ContextQualityService
from backend.src.services.coverage_guidance_service import CoverageGuidanceService
from backend.src.services.layperson_answer_service import LaypersonAnswerService
from backend.src.services.layperson_post_llm_service import LaypersonPostLlmService
from backend.src.services.layperson_topic_service import LaypersonTopicMatch
from backend.src.services.legal_extractive_answer_service import LegalExtractiveAnswerService
from backend.src.services.legal_extractive_decision import should_use_extractive_answer
from backend.src.services.llm_service import LlmService
from backend.src.services.question_intent_service import QuestionIntentAnalysis, QuestionIntentService
from backend.src.services.source_consistency_service import SourceConsistencyService
from backend.src.services.topic_intent_gate_service import TopicIntentGateService
from backend.src.utils.question_chunk_relevance import question_matches_chunks
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.query import QueryRequest


class AnswerBundleService:
    """Orchestrates answer generation, templates, and layperson post-processing."""

    def __init__(self) -> None:
        self._llm = LlmService()
        self._intent = QuestionIntentService()
        self._topic_gate = TopicIntentGateService()
        self._specificity_guard = AnswerSpecificityGuardService()
        self._adequacy = ContextAdequacyService()
        self._context_quality = ContextQualityService()
        self._coverage_guidance = CoverageGuidanceService()
        self._assembly = AnswerBundleAssemblyService()
        self._source_consistency = SourceConsistencyService()
        self._templates = AnswerTemplateBundleService()
        self._layperson = LaypersonAnswerService()
        self._post_llm = LaypersonPostLlmService()
        self._extractive = LegalExtractiveAnswerService()
        self._extractive_bundle = AnswerExtractiveBundleService()

    async def build(
        self,
        request: QueryRequest,
        chunks: list[dict[str, Any]],
        retrieval_route: str | None,
        history: list[dict] | None,
    ) -> dict[str, Any]:
        intent = self._intent.analyze(request.question)
        if self._adequacy.is_out_of_scope_national_law(request.question):
            guidance = self._coverage_guidance.resolve(request.question)
            return self._assembly.insufficient_bundle(
                request, retrieval_route, "topic_not_in_corpus", intent, guidance,
            )
        context_quality = self._context_quality.assess(chunks, request.question)
        prefer_rag = request.audience == "professional" or intent.requires_rag_pipeline
        topic_bundle = self._try_topic_template(request, intent)
        if context_quality.is_usable and prefer_rag:
            extractive_bundle = self._extractive_bundle.try_build(request, chunks, retrieval_route)
            if extractive_bundle:
                return extractive_bundle
        if topic_bundle and not prefer_rag:
            return topic_bundle
        if context_quality.is_usable:
            extractive_bundle = self._extractive_bundle.try_build(request, chunks, retrieval_route)
            if extractive_bundle:
                return extractive_bundle
        if topic_bundle:
            return topic_bundle
        if not context_quality.is_usable:
            topic_bundle = self._try_topic_template(request, intent, force=True)
            if topic_bundle:
                return topic_bundle
            cn_bundle = self._try_cn_fallback(request)
            if cn_bundle:
                return cn_bundle
            guidance = self._coverage_guidance.resolve(request.question)
            return self._assembly.insufficient_bundle(
                request, retrieval_route, "low_confidence", intent, guidance,
            )
        adequacy = self._adequacy.assess(
            request.question, chunks, retrieval_route, request.filters, request.audience,
        )
        if not adequacy.is_adequate:
            return self._resolve_inadequate(request, chunks, retrieval_route, adequacy, intent)
        if request.query_mode == "compare" and not self._has_compare_sources(chunks):
            guidance = self._coverage_guidance.resolve(request.question)
            return self._assembly.compare_gap_bundle(request, retrieval_route, guidance)
        if not question_matches_chunks(request.question, chunks):
            return self._resolve_mismatch(request, chunks, retrieval_route, intent)
        return await self._generate_llm_bundle(request, chunks, retrieval_route, history, intent)

    async def _generate_llm_bundle(
        self,
        request: QueryRequest,
        chunks: list[dict],
        retrieval_route: str | None,
        history: list[dict] | None,
        intent: QuestionIntentAnalysis,
    ) -> dict[str, Any]:
        use_specific_prompt = intent.requires_rag_pipeline and request.audience == "professional"
        answer_text, citations = await self._llm.generate_answer(
            request.question, chunks, history, request.query_mode, request.audience,
            context_quality="hoog", specific_intent=use_specific_prompt,
        )
        citations = self._source_consistency.filter_citations(citations, chunks)
        used_extractive = False
        if request.audience == "layperson":
            extractive = self._extractive.build_layperson_answer(request.question, chunks)
            if extractive and should_use_extractive_answer(
                answer_text, chunks, request.audience, request.question,
            ):
                answer_text = extractive
                used_extractive = True
            else:
                answer_text = self._layperson.format(answer_text, request.question, chunks)
        else:
            extractive = self._extractive.build_professional_answer(request.question, chunks)
            if extractive and should_use_extractive_answer(
                answer_text, chunks, request.audience, request.question,
            ):
                answer_text = extractive
                used_extractive = True
        if use_specific_prompt and self._specificity_guard.violates_rules(answer_text, intent):
            extractive_bundle = self._extractive_bundle.try_build(request, chunks, retrieval_route)
            if extractive_bundle:
                return extractive_bundle
            guidance = self._coverage_guidance.resolve(request.question)
            adequacy = AdequacyResult(
                is_adequate=False, reason="topic_not_in_corpus", coverage_status="insufficient",
            )
            return self._assembly.gap_bundle(request, chunks, retrieval_route, adequacy, guidance, intent)
        if request.audience == "layperson" and not used_extractive:
            weak_bundle = self._post_llm.resolve_weak_answer(
                request, answer_text, intent, self._topic_gate, self._build_topic_bundle,
                self._try_cn_fallback, lambda req: self._weak_llm_gap(req, chunks, retrieval_route, intent),
            )
            if weak_bundle:
                return weak_bundle
        return self._assembly.finalize(
            request, answer_text, citations, chunks, retrieval_route,
            AdequacyResult(is_adequate=True, coverage_status="adequate"), None,
        )

    def _resolve_inadequate(
        self,
        request: QueryRequest,
        chunks: list[dict],
        route: str | None,
        adequacy: AdequacyResult,
        intent: QuestionIntentAnalysis,
    ) -> dict[str, Any]:
        extractive_bundle = self._extractive_bundle.try_build(request, chunks, route)
        if extractive_bundle:
            return extractive_bundle
        topic_bundle = self._try_topic_template(request, intent, force=True)
        if topic_bundle:
            return topic_bundle
        cn_bundle = self._try_cn_fallback(request)
        if cn_bundle:
            return cn_bundle
        guidance = self._coverage_guidance.resolve(request.question)
        return self._assembly.gap_bundle(request, chunks, route, adequacy, guidance, intent)

    def _resolve_mismatch(
        self,
        request: QueryRequest,
        chunks: list[dict],
        route: str | None,
        intent: QuestionIntentAnalysis,
    ) -> dict[str, Any]:
        extractive_bundle = self._extractive_bundle.try_build(request, chunks, route)
        if extractive_bundle:
            return extractive_bundle
        topic_bundle = self._try_topic_template(request, intent, force=True)
        if topic_bundle:
            return topic_bundle
        cn_bundle = self._try_cn_fallback(request)
        if cn_bundle:
            return cn_bundle
        mismatch = AdequacyResult(
            is_adequate=False, reason="irrelevant_retrieval", coverage_status="insufficient",
        )
        guidance = self._coverage_guidance.resolve(request.question)
        return self._assembly.gap_bundle(request, chunks, route, mismatch, guidance, intent)

    def _try_topic_template(
        self,
        request: QueryRequest,
        intent: QuestionIntentAnalysis,
        force: bool = False,
    ) -> dict[str, Any] | None:
        del force
        parts = self._templates.try_topic_template(request)
        if parts is None:
            return None
        match, answer_text, citations, stub_chunks, confidence = parts
        if self._topic_gate.should_block_topic_template(request, intent, match.topic_id):
            return None
        return self._assembly.finalize(
            request, answer_text, citations, stub_chunks,
            AnswerTemplateBundleService.topic_route(),
            AnswerTemplateBundleService.topic_adequacy(), None, confidence=confidence,
        )

    def _build_topic_bundle(self, request: QueryRequest, match: LaypersonTopicMatch) -> dict[str, Any]:
        answer_text, citations, stub_chunks, confidence = self._templates.build_topic_from_match(
            request, match,
        )
        return self._assembly.finalize(
            request, answer_text, citations, stub_chunks,
            AnswerTemplateBundleService.topic_route(),
            AnswerTemplateBundleService.topic_adequacy(), None, confidence=confidence,
        )

    def _try_cn_fallback(self, request: QueryRequest) -> dict[str, Any] | None:
        parts = self._templates.try_cn_fallback(request)
        if parts is None:
            return None
        _, answer_text, citations, stub_chunks, confidence = parts
        return self._assembly.finalize(
            request, answer_text, citations, stub_chunks,
            AnswerTemplateBundleService.cn_route(),
            AnswerTemplateBundleService.topic_adequacy(), None, confidence=confidence,
        )

    def _weak_llm_gap(
        self,
        request: QueryRequest,
        chunks: list[dict],
        route: str | None,
        intent: QuestionIntentAnalysis,
    ) -> dict[str, Any]:
        adequacy = AdequacyResult(
            is_adequate=False, reason="topic_not_in_corpus", coverage_status="insufficient",
        )
        guidance = self._coverage_guidance.resolve(request.question)
        return self._assembly.gap_bundle(request, chunks, route, adequacy, guidance, intent)

    def _has_compare_sources(self, chunks: list[dict]) -> bool:
        celexes = {chunk.get("celex") for chunk in chunks if chunk.get("celex")}
        return len(celexes) >= 2
