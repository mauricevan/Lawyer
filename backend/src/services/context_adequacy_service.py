"""Detect when retrieved context cannot reliably answer the question."""

from backend.src.services.celex_discovery_service import CelexDiscoveryService
from ingestion.src.data.legal_term_hints import match_primary_celex_hint
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.query import QueryFilters

from backend.src.services.answer_confidence_service import (
    LOW_CONFIDENCE_THRESHOLD,
    AnswerConfidenceService,
)
from shared.config.coverage_guidance_loader import (
    get_coverage_topics,
    get_mismatch_config,
    get_topic_gate_exclude_patterns,
)

MIN_RELEVANCE_SCORE = 0.35
_NATIONAL_LAW_PATTERNS = (
    "nederlandse wet", "vakantiedagen", "nl wet", "nederlands recht",
    "minimumloon", "wettelijk minimumloon", "belgisch recht", "parkeerboete",
    "parkeerboetes", "celstraf", "belastingfraude", "standplaatsvergunning",
    "gemeentelijke afval", "afvalstoffenheffing", "waterschapsbelasting",
    "studiefinanciering", "duos regels", "notaris kosten", "alleen nederland",
)
_SENSITIVE_TOPIC_IDS = frozenset({"workplace_monitoring", "employee_data_privacy"})
_PROFESSIONAL_QUERY_SIGNALS = ("high-risk", "high risk", "risicovol", "ai act", "32024r1689")
_PROFESSIONAL_CHUNK_SIGNALS = (
    "high-risk", "high risk", "risico", "bijlage", "annex", "32024r1689", "intelligentie",
)


class ContextAdequacyService:
    """Rule-based gate before LLM answer generation."""

    def __init__(self) -> None:
        self._confidence = AnswerConfidenceService()

    def is_out_of_scope_national_law(self, question: str) -> bool:
        """True when the question is clearly outside EU corpus scope."""
        return self._is_national_law_question(question)

    def assess(
        self,
        question: str,
        chunks: list[dict],
        retrieval_route: str | None = None,
        filters: QueryFilters | None = None,
        audience: str = "layperson",
    ) -> AdequacyResult:
        retrieval_score = self._confidence.assess_retrieval(chunks, retrieval_route)
        if not chunks:
            return self._inadequate("no_chunks", "insufficient")
        if self._is_national_law_question(question):
            return self._inadequate("topic_not_in_corpus", "insufficient")
        if retrieval_score < LOW_CONFIDENCE_THRESHOLD:
            return self._inadequate("low_confidence", "insufficient")
        if self._has_intent_mismatch(question, filters):
            return self._inadequate("irrelevant_retrieval", "irrelevant")
        if not self._meets_relevance_score(chunks):
            return self._inadequate("low_confidence", "insufficient")
        if audience == "professional" and self._professional_context_gap(question, chunks):
            return self._inadequate("low_confidence", "insufficient")
        if self._topic_not_in_corpus(question, chunks):
            return self._inadequate("topic_not_in_corpus", "irrelevant")
        return AdequacyResult(is_adequate=True, coverage_status="adequate")

    def _professional_context_gap(self, question: str, chunks: list[dict]) -> bool:
        lowered = question.lower()
        if not any(signal in lowered for signal in _PROFESSIONAL_QUERY_SIGNALS):
            return False
        corpus_text = " ".join(
            f"{chunk.get('title', '')} {chunk.get('text', '')} {chunk.get('celex', '')}"
            for chunk in chunks
        ).lower()
        return not any(signal in corpus_text for signal in _PROFESSIONAL_CHUNK_SIGNALS)

    def _is_national_law_question(self, question: str) -> bool:
        lowered = question.lower()
        return any(pattern in lowered for pattern in _NATIONAL_LAW_PATTERNS)

    def _inadequate(self, reason: str, status: str) -> AdequacyResult:
        return AdequacyResult(
            is_adequate=False,
            reason=reason,  # type: ignore[arg-type]
            coverage_status=status,  # type: ignore[arg-type]
        )

    def _has_intent_mismatch(self, question: str, filters: QueryFilters | None) -> bool:
        config = get_mismatch_config()
        signals = config.get("surveillance_signals", [])
        irrelevant_ids = set(config.get("irrelevant_intent_ids", []))
        if not filters or filters.intent_id not in irrelevant_ids:
            return False
        lowered = question.lower()
        return any(signal in lowered for signal in signals)

    def _meets_relevance_score(self, chunks: list[dict]) -> bool:
        scores = [
            float(chunk.get("rerank_score") or chunk.get("score") or 0.0)
            for chunk in chunks
        ]
        return max(scores, default=0.0) >= MIN_RELEVANCE_SCORE

    def _topic_not_in_corpus(self, question: str, chunks: list[dict]) -> bool:
        lowered = question.lower()
        if any(pattern in lowered for pattern in get_topic_gate_exclude_patterns()):
            return False
        celex_hint = match_primary_celex_hint(question)
        if not celex_hint:
            celex_hint = CelexDiscoveryService().high_confidence_celex(question)
        if celex_hint and any(str(chunk.get("celex", "")) == celex_hint for chunk in chunks):
            return False
        topic = self._match_topic(question)
        if not topic or topic.get("id") not in _SENSITIVE_TOPIC_IDS:
            return False
        if topic.get("id") == "employee_data_privacy":
            if any(term in lowered for term in ("webshop", "webwinkel", "consument", "e-commerce")):
                return False
        if topic.get("id") == "workplace_monitoring":
            surveillance = get_mismatch_config().get("surveillance_signals", [])
            if not any(str(signal).lower() in lowered for signal in surveillance):
                return False
            if any(str(chunk.get("celex", "")) == "32016R0679" for chunk in chunks):
                return False
        keywords = [str(k).lower() for k in topic.get("chunk_keywords", [])]
        if not keywords:
            return False
        corpus_text = " ".join(
            f"{chunk.get('title', '')} {chunk.get('text', '')}" for chunk in chunks
        ).lower()
        return not any(keyword in corpus_text for keyword in keywords)

    def _match_topic(self, question: str) -> dict | None:
        lowered = question.lower()
        for topic in get_coverage_topics():
            if topic.get("id") == "fallback_general":
                continue
            patterns = topic.get("patterns", [])
            if any(str(p).lower() in lowered for p in patterns):
                return topic
        return None
