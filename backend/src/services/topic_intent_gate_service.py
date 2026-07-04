"""Gate layperson topic templates by question intent (system instruction v1.0)."""
from backend.src.services.question_intent_service import QuestionIntentAnalysis, QuestionIntentService
from shared.schemas.query import QueryRequest


class TopicIntentGateService:
    """Decides when topic templates must not replace RAG/article answers."""

    def __init__(self) -> None:
        self._intent = QuestionIntentService()

    def should_block_topic_template(
        self,
        request: QueryRequest,
        intent: QuestionIntentAnalysis,
        topic_id: str | None,
    ) -> bool:
        if intent.question_type == "article_lookup":
            return True
        if topic_id and self._intent.is_registry_intro_topic(topic_id):
            if intent.requires_rag_pipeline or intent.specificity == "specific":
                return True
        if request.audience == "professional" and intent.requires_rag_pipeline:
            return True
        return False
