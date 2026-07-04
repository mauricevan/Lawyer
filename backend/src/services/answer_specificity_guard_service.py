"""Post-generation checks for specific EU legal questions."""
from backend.src.services.question_intent_service import QuestionIntentAnalysis, QuestionIntentService


class AnswerSpecificityGuardService:
    """Blocks generic registry intros when a specific answer was required."""

    def __init__(self) -> None:
        self._intent = QuestionIntentService()

    def violates_rules(self, answer: str, intent: QuestionIntentAnalysis) -> bool:
        if not intent.requires_rag_pipeline:
            return False
        lowered = answer.lower()
        if self._has_legal_basis_section(lowered):
            return False
        forbidden = self._intent.forbidden_generic_phrases()
        return any(phrase.lower() in lowered for phrase in forbidden)

    def _has_legal_basis_section(self, lowered_answer: str) -> bool:
        if "## wettelijke grondslag" in lowered_answer:
            return True
        return "| artikel |" in lowered_answer or "art. " in lowered_answer
