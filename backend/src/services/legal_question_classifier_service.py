"""Legal question classifier — 3-layer interpretation before retrieval (V3)."""
from dataclasses import dataclass

from backend.src.utils.legal_domain_inference import LegalRoutingDomain, infer_legal_domain
from backend.src.utils.legal_question_interpretation import LegalActor, infer_legal_actor
from backend.src.utils.legal_question_type_inference import LegalQuestionType, infer_legal_question_type


@dataclass(frozen=True)
class LegalQuestionClassification:
    """Three-layer classifier output — mandatory before retrieval."""

    legal_actor: LegalActor
    legal_domain: LegalRoutingDomain
    legal_question_type: LegalQuestionType


def classify_legal_question(question: str) -> LegalQuestionClassification:
    """Classify actor, domain, and question type from question text only."""
    actor = infer_legal_actor(question)
    domain = infer_legal_domain(question, actor)
    question_type = infer_legal_question_type(question, actor, domain)
    return LegalQuestionClassification(
        legal_actor=actor,
        legal_domain=domain,
        legal_question_type=question_type,
    )
