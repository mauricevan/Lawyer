"""Build clarify/gap bundles for the declarant pipeline."""
from backend.src.services.clarification_question_service import ClarificationQuestionService
from backend.src.utils.clarification_formatter import (
    clarification_prompt_from_result,
    format_clarification_section,
    verification_questions_from_result,
)
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from shared.legal.disclaimers import get_disclaimer
from shared.schemas.legal_clarification import LegalClarificationResult
from shared.schemas.query import QueryRequest


class DeclarantResponseBuilder:
    """User-facing bundles for clarify and gap outcomes."""

    def __init__(self) -> None:
        self._questions = ClarificationQuestionService()
        self._ilcl = LegalClarificationOrchestrator()

    def clarify_bundle(
        self,
        request: QueryRequest,
        result: LegalClarificationResult,
    ) -> dict:
        questions = verification_questions_from_result(result, request.audience)
        prompt = clarification_prompt_from_result(result)
        quality: dict = {
            "confidence_score": 0.0,
            "verification_questions": questions,
        }
        if prompt:
            quality["clarification_prompt"] = prompt
        status = "clarify_only" if result.state != "unanswerable" else "irrelevant"
        return {
            "answer_text": result.formatted_section,
            "citations": [],
            "disclaimer": get_disclaimer(request.audience, request.language),  # type: ignore[arg-type]
            "quality": quality,
            "coverage_guidance": None,
            "coverage_status": status,
        }

    def fetch_clarify_bundle(self, request: QueryRequest, question: str) -> dict:
        """Ask for more detail when EUR-Lex fetch returned nothing usable."""
        items = self._questions.build(
            ["onvoldoende detail voor gerichte EUR-Lex-zoekopdracht"],
            request.audience,
            question,
        )
        result = LegalClarificationResult(
            state="ambiguous",
            mode="questions",
            enriched_question=question,
            ambiguity_score=0.8,
            ambiguity_reasons=["fetch_insufficient"],
            questions=items,
            should_proceed=False,
        )
        section = format_clarification_section(result, request.audience)
        return self.clarify_bundle(request, result.model_copy(update={"formatted_section": section}))

    def gap_bundle(self, request: QueryRequest, reason: str) -> dict:
        text = (
            "## Kort antwoord\n"
            "Ik kon dit niet met zekerheid onderbouwen vanuit EUR-Lex. "
            f"{reason}\n\n"
            "## Wat u wél kunt doen\n"
            "- Formuleer de vraag met meer context (wie, wat, welke situatie).\n"
            "- Zoek direct op [EUR-Lex](https://eur-lex.europa.eu/).\n"
            "- Raadpleeg een gekwalificeerd jurist bij twijfel."
        )
        return {
            "answer_text": text,
            "citations": [],
            "disclaimer": get_disclaimer(request.audience, request.language),  # type: ignore[arg-type]
            "quality": {"confidence_score": 0.0, "verification_questions": []},
            "coverage_guidance": None,
            "coverage_status": "insufficient",
        }
