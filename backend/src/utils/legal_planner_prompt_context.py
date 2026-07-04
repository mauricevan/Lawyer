"""Build planner prompt context from 3-layer classification (V3)."""
from backend.src.services.legal_question_classifier_service import classify_legal_question

_DOMAIN_LABELS = {
    "internal_market": "interne markt / lidstaatafwijkingen / harmonisatie",
    "consumer_protection": "consumentenbescherming",
    "employment_law": "arbeidsrecht / gelijke behandeling",
    "administrative_law": "handhaving / markttoezicht",
    "product_safety": "productveiligheid / CE / conformiteit",
    "data_protection": "AVG / gegevensbescherming",
    "digital_services": "DSA (alleen bij expliciete platform/content-vraag)",
    "unknown": "onbekend",
}


def build_planner_interpretation_hints(question: str) -> str:
    """Return Dutch hints block for the legal planner user prompt."""
    classification = classify_legal_question(question)
    domain_label = _DOMAIN_LABELS.get(classification.legal_domain, classification.legal_domain)
    return "\n".join([
        "Interpretatie (verplicht vóór retrieval — domain first):",
        f"- legal_actor: {classification.legal_actor}",
        f"- legal_domain: {classification.legal_domain} ({domain_label})",
        f"- legal_question_type: {classification.legal_question_type}",
        "- Geen keyword→document routing; geen DSA/GDPR tenzij domain expliciet klopt.",
    ])
