"""Build deterministic answer bundles from topic and CN classification templates."""
from typing import Any

from backend.src.services.cn_classification_answer_service import CnClassificationAnswerService
from backend.src.services.cn_classification_service import CnClassificationService, CnPositionMatch
from backend.src.services.layperson_topic_answer_service import LaypersonTopicAnswerService
from backend.src.services.layperson_topic_service import LaypersonTopicMatch, LaypersonTopicService
from shared.schemas.citation import Citation
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.query import QueryRequest

_CN_CLASSIFICATION_CONFIDENCE = 0.55
_TOPIC_TEMPLATE_CONFIDENCE = 0.62


class AnswerTemplateBundleService:
    """Topic and CN template bundles shared by AnswerBundleService."""

    def __init__(self) -> None:
        self._layperson_topic = LaypersonTopicService()
        self._layperson_topic_answer = LaypersonTopicAnswerService()
        self._cn_classification = CnClassificationService()
        self._cn_answer = CnClassificationAnswerService()

    def try_topic_template(
        self,
        request: QueryRequest,
    ) -> tuple[LaypersonTopicMatch, str, list[Citation], list[dict], float] | None:
        if request.audience != "layperson":
            return None
        match = self._layperson_topic.match(request.question)
        if match is None:
            return None
        return self._topic_parts(request, match)

    def try_cn_fallback(
        self, request: QueryRequest,
    ) -> tuple[CnPositionMatch, str, list[Citation], list[dict], float] | None:
        cn_match = self._cn_classification.resolve(request.question)
        if not cn_match:
            return None
        return self._cn_parts(request, cn_match)

    def build_topic_from_match(
        self, request: QueryRequest, match: LaypersonTopicMatch,
    ) -> tuple[str, list[Citation], list[dict], float]:
        _, answer_text, citations, stub_chunks, confidence = self._topic_parts(request, match)
        return answer_text, citations, stub_chunks, confidence

    def _topic_parts(
        self, request: QueryRequest, match: LaypersonTopicMatch,
    ) -> tuple[LaypersonTopicMatch, str, list[Citation], list[dict], float]:
        answer_text = self._layperson_topic_answer.build(match, request.audience)
        stub_chunks = [{
            "celex": match.regulation_celex,
            "title": match.regulation_title,
            "text": match.summary_nl,
        }]
        citations = [Citation(
            celex=match.regulation_celex,
            title=match.regulation_title,
            excerpt=match.summary_nl[:400],
            eurlex_url=f"https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:{match.regulation_celex}",
        )]
        return match, answer_text, citations, stub_chunks, _TOPIC_TEMPLATE_CONFIDENCE

    def _cn_parts(
        self, request: QueryRequest, cn_match: CnPositionMatch,
    ) -> tuple[CnPositionMatch, str, list[Citation], list[dict], float]:
        answer_text = self._cn_answer.build(cn_match, request.audience)
        stub_chunks = [{
            "celex": cn_match.regulation_celex,
            "title": cn_match.regulation_title,
            "text": cn_match.summary_nl,
        }]
        citations = [Citation(
            celex=cn_match.regulation_celex,
            title=cn_match.regulation_title,
            excerpt=cn_match.summary_nl[:400],
            eurlex_url=(
                f"https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:{cn_match.regulation_celex}"
            ),
        )]
        return cn_match, answer_text, citations, stub_chunks, _CN_CLASSIFICATION_CONFIDENCE

    @staticmethod
    def topic_route() -> str:
        return "layperson_topic"

    @staticmethod
    def cn_route() -> str:
        return "cn_classification"

    @staticmethod
    def topic_adequacy() -> AdequacyResult:
        return AdequacyResult(is_adequate=True, coverage_status="adequate")
