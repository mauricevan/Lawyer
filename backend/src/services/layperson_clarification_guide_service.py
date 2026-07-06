"""Conversation-first layperson clarification — one gap, contextual options only."""
from backend.src.services.domain_fallback_classifier_service import classify_primary_domain
from backend.src.utils.clarification_patterns import (
    AI_REGISTRATION_HINTS,
    COMMERCE_HINTS,
    DATA_STORAGE_HINTS,
    EMPLOYMENT_HINTS,
    IDENTIFICATION_HINTS,
    PLATFORM_START_HINTS,
    PRIVACY_HINTS,
)
from backend.src.utils.question_typo_normalizer import normalize_question_typos
from shared.schemas.legal_clarification import ClarificationQuestion


class LaypersonClarificationGuideService:
    """Guide laypersons like a professional assistant: one clear follow-up at a time."""

    def build(self, question: str, reasons: list[str]) -> ClarificationQuestion:
        """Return exactly one contextual clarification question."""
        normalized = normalize_question_typos(question)
        topic = self._detect_topic(normalized)
        if topic == "platform":
            return self._platform_type()
        if topic == "data_storage":
            return self._data_storage()
        if topic == "identification":
            return self._identification()
        if topic == "privacy":
            return self._privacy()
        if topic == "employment":
            return self._employment()
        if topic == "commerce":
            return self._commerce()
        if "geen actor" in reasons and topic == "general":
            return self._actor()
        return self._open_context()

    def _detect_topic(self, question: str) -> str:
        lowered = question.lower()
        if any(h in lowered for h in PLATFORM_START_HINTS) or "platform" in lowered or "platfrom" in lowered:
            return "platform"
        if any(h in lowered for h in DATA_STORAGE_HINTS):
            return "data_storage"
        if any(h in lowered for h in IDENTIFICATION_HINTS):
            return "identification"
        if any(h in lowered for h in AI_REGISTRATION_HINTS):
            return self._resolve_ai_registration_topic(lowered=lowered)
        if any(h in lowered for h in PRIVACY_HINTS):
            return "privacy"
        if any(h in lowered for h in EMPLOYMENT_HINTS):
            return "employment"
        if any(h in lowered for h in COMMERCE_HINTS):
            return "commerce"
        fallback = classify_primary_domain(question)
        if fallback != "onzeker":
            return fallback
        return "general"

    def _resolve_ai_registration_topic(self, *, lowered: str) -> str:
        """Route AI/tool registration via substance, not blanket privacy."""
        domain = classify_primary_domain(lowered)
        return domain if domain != "onzeker" else "platform"

    def _platform_type(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="platform_type",
            prompt="Wat voor platform of online dienst bedoelt u?",
            options=["marktplaats", "social media", "app / SaaS", "contentwebsite"],
        )

    def _data_storage(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="data_storage_context",
            prompt="Wat is uw situatie rond het opslaan of verwerken van gegevens?",
            options=[
                "Ik ben bedrijf dat gegevens van anderen opslaat",
                "Een bedrijf bewaart mijn gegevens",
                "Ik geef gegevens door aan andere partijen",
                "Data wordt buiten de EU opgeslagen",
            ],
        )

    def _identification(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="identification_context",
            prompt="Waarvoor moet u zich legitimeren of identificeren?",
            options=[
                "online account / app",
                "bank of betaling",
                "overheidsdienst / formulier",
                "zakelijk (KYC)",
            ],
        )

    def _privacy(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="privacy_context",
            prompt="Waar gaat het concreet om met uw gegevens?",
            options=[
                "website / cookies",
                "app op telefoon",
                "gegevens van klanten (bedrijf)",
                "gegevens doorgeven aan anderen",
            ],
        )

    def _employment(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="employment_context",
            prompt="Wat is uw situatie op het werk?",
            options=["loon of uren", "ontslag", "contract", "veiligheid op werk"],
        )

    def _commerce(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="commerce_context",
            prompt="Wat voor aankoop of verkoop bedoelt u?",
            options=["online webshop", "marktplaats", "abonnement", "retour of garantie"],
        )

    def _actor(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="actor",
            prompt="Wat is uw rol in deze situatie?",
            options=["ondernemer", "consument / particulier", "organisatie / overheid"],
        )

    def _scope(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="scope",
            prompt="Richt u zich op de EU, één lidstaat of wereldwijd?",
            options=["EU-breed", "één lidstaat", "wereldwijd"],
        )

    def _open_context(self) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="context",
            prompt="Kunt u in één zin beschrijven wat u precies doet of wat er speelt?",
            options=[],
        )
