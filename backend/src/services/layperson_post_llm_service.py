"""Post-LLM layperson fallback when formatted answer is hybrid boilerplate."""
from typing import Any, Callable

from backend.src.services.layperson_topic_service import LaypersonTopicMatch, LaypersonTopicService
from backend.src.services.question_intent_service import QuestionIntentAnalysis
from backend.src.services.topic_intent_gate_service import TopicIntentGateService
from backend.src.utils.layperson_answer_formatter import is_hybrid_boilerplate
from shared.schemas.query import QueryRequest


class LaypersonPostLlmService:
    """Routes hybrid-boilerplate LLM answers to topic, CN, or gap bundles."""

    def __init__(self) -> None:
        self._layperson_topic = LaypersonTopicService()

    def resolve_weak_answer(
        self,
        request: QueryRequest,
        answer_text: str,
        intent: QuestionIntentAnalysis,
        topic_gate: TopicIntentGateService,
        build_topic: Callable[[QueryRequest, LaypersonTopicMatch], dict[str, Any]],
        build_cn: Callable[[QueryRequest], dict[str, Any] | None],
        build_gap: Callable[[QueryRequest], dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Return replacement bundle when answer is boilerplate; None if acceptable."""
        if request.audience != "layperson" or not is_hybrid_boilerplate(answer_text):
            return None
        topic_match = self._layperson_topic.match(request.question)
        if topic_match and not topic_gate.should_block_topic_template(
            request, intent, topic_match.topic_id,
        ):
            return build_topic(request, topic_match)
        cn_bundle = build_cn(request)
        if cn_bundle:
            return cn_bundle
        return build_gap(request)
