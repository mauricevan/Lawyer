"""Verification prompts when retrieval confidence is low."""
from shared.schemas.query import QueryRequest

from backend.src.services.answer_confidence_service import AnswerConfidenceService


class VerificationQuestionService:
    """Builds follow-up checks for uncertain answers."""

    def __init__(self) -> None:
        self._confidence = AnswerConfidenceService()

    def build(
        self,
        request: QueryRequest,
        confidence: float,
        retrieval_route: str | None,
    ) -> list[str]:
        if not self._confidence.is_low(confidence):
            return []
        if request.audience == "professional":
            return self._professional_questions(request, retrieval_route)
        return self._layperson_questions(request, retrieval_route)

    def _layperson_questions(self, request: QueryRequest, route: str | None) -> list[str]:
        questions = [
            "Welke EU-wet of regeling bedoelt u precies (bijv. GDPR, AI Act)?",
            "Gaat het om regels die nu gelden of om een oudere versie?",
        ]
        if route == "live_fallback":
            questions.append("Kunt u de bron op EUR-Lex zelf nakijken? Het antwoord is mogelijk onvolledig.")
        if request.query_mode == "compliance":
            questions.append("Geldt dit voor uw bedrijfstype of sector? Dat kan het antwoord wijzigen.")
        return questions[:3]

    def _professional_questions(self, request: QueryRequest, route: str | None) -> list[str]:
        questions = [
            "Welke CELEX en artikelen zijn leidend voor uw dossier?",
            "Is de geconsolideerde versie en inwerkingtreding gecontroleerd op EUR-Lex?",
        ]
        if route == "live_fallback":
            questions.append("Bevat de live fallback voldoende context of is handmatige CELLAR-verificatie nodig?")
        if request.query_mode == "compare":
            questions.append("Zijn alle te vergelijken instrumenten in dezelfde taalversie opgenomen?")
        return questions[:3]
