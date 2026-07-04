"""Attach 3-layer classification to interpretation plans."""
from backend.src.services.legal_question_classifier_service import classify_legal_question
from shared.schemas.legal_interpretation import LegalInterpretationPlan


def apply_context_to_plan(plan: LegalInterpretationPlan, question: str) -> LegalInterpretationPlan:
    """Fill actor/domain/question_type from classifier when planner left them unknown."""
    classification = classify_legal_question(question)
    return plan.model_copy(update={
        "legal_actor": (
            classification.legal_actor
            if plan.legal_actor == "unknown"
            else plan.legal_actor
        ),
        "legal_domain": (
            classification.legal_domain
            if plan.legal_domain == "unknown"
            else plan.legal_domain
        ),
        "legal_question_type": (
            classification.legal_question_type
            if plan.legal_question_type == "unknown"
            else plan.legal_question_type
        ),
    })
