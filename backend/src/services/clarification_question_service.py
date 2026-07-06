"""V10.3 ILCL mode 1 — targeted clarification questions."""
from backend.src.services.layperson_clarification_guide_service import LaypersonClarificationGuideService
from backend.src.utils.clarification_patterns import PLATFORM_START_HINTS
from shared.schemas.legal_clarification import ClarificationQuestion


class ClarificationQuestionService:
    """Build clarification questions from ambiguity reasons and question topic."""

    def __init__(self) -> None:
        self._layperson_guide = LaypersonClarificationGuideService()

    def build(
        self,
        reasons: list[str],
        audience: str = "layperson",
        question: str = "",
    ) -> list[ClarificationQuestion]:
        """Return ordered questions based on detected gaps and topic."""
        if audience == "layperson":
            return [self._layperson_guide.build(question, reasons)]

        topic = self._detect_topic(question)
        questions: list[ClarificationQuestion] = []
        if topic == "data_storage":
            questions.append(self._data_storage_context(audience))
        elif topic == "identification":
            questions.append(self._identification_context(audience))
        elif topic == "privacy":
            questions.append(self._privacy_context(audience))
        elif topic == "employment":
            questions.append(self._employment_context(audience))
        elif topic == "commerce":
            questions.append(self._commerce_context(audience))
        elif "platform-start zonder detail" in reasons or self._is_platform_question(question):
            questions.append(self._platform_type(audience))
        elif "geen activiteit" in reasons:
            questions.append(self._situation_context(audience))
        if "geen actor" in reasons and topic != "identification":
            questions.append(self._actor(audience))
        if "geen geografische context" in reasons:
            questions.append(self._scope(audience))
        if "meerdere EU-domeinen mogelijk" in reasons and len(questions) < 3:
            questions.append(self._focus(audience))
        if not questions:
            questions.append(self._generic(audience))
        return questions[:3]

    def _detect_topic(self, question: str) -> str:
        return self._layperson_guide._detect_topic(question)  # noqa: SLF001

    def _is_platform_question(self, question: str) -> bool:
        lowered = question.lower()
        return (
            any(h in lowered for h in PLATFORM_START_HINTS)
            or "platform" in lowered
            or "platfrom" in lowered
        )

    def _identification_context(self, audience: str) -> ClarificationQuestion:
        opts = [
            "online account / app", "bank of betaling", "reizen binnen EU",
            "overheidsdienst / formulier", "zakelijk (KYC)",
        ]
        prompt = "Waarvoor moet u zich legitimeren of identificeren?"
        if audience != "layperson":
            prompt = "Which identification or KYC context applies?"
        return ClarificationQuestion(id="identification_context", prompt=prompt, options=opts)

    def _privacy_context(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="privacy_context",
            prompt="Waar gaat het om met uw gegevens?",
            options=["website / cookies", "app op telefoon", "gegevens van klanten (bedrijf)", "gegevens doorgeven aan anderen"],
        )

    def _data_storage_context(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="data_storage_context",
            prompt="Wat is uw situatie rond het opslaan of verwerken van data?",
            options=[
                "Ik ben bedrijf dat gegevens van anderen opslaat",
                "Een bedrijf bewaart mijn gegevens",
                "Ik geef gegevens door aan andere partijen",
                "Data wordt buiten de EU opgeslagen",
            ],
        )

    def _employment_context(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="employment_context",
            prompt="Wat is uw situatie op het werk?",
            options=["loon of uren", "ontslag", "contract", "veiligheid op werk"],
        )

    def _commerce_context(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="commerce_context",
            prompt="Wat voor aankoop of verkoop bedoelt u?",
            options=["online webshop", "marktplaats", "abonnement", "retour of garantie"],
        )

    def _situation_context(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="situation_context",
            prompt="Welke situatie beschrijft uw vraag het best?",
            options=["online / app", "winkel of dienst", "werk of school", "reizen", "overheid"],
        )

    def _platform_type(self, audience: str) -> ClarificationQuestion:
        opts = ["marktplaats", "social media", "app / SaaS", "contentwebsite"]
        if audience == "professional":
            opts = ["online marketplace", "intermediary platform (DSA)", "SaaS", "publisher site"]
        return ClarificationQuestion(id="platform_type", prompt="Wat voor platform bedoel u?", options=opts)

    def _actor(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="actor",
            prompt="Bent u ondernemer, gebruiker of een organisatie?" if audience == "layperson"
            else "Wat is uw rol (operator, onderneming, overheid)?",
            options=["ondernemer", "gebruiker", "organisatie"],
        )

    def _scope(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="scope",
            prompt="Richt u zich op de EU, één lidstaat of wereldwijd?",
            options=["EU-breed", "één lidstaat", "wereldwijd"],
        )

    def _focus(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="legal_focus",
            prompt="Waar ligt uw hoofdzorg: vergunningen, gebruikersregels of consumentenrecht?",
            options=["vergunningen", "platformregels (DSA)", "consumentenrecht"],
        )

    def _generic(self, audience: str) -> ClarificationQuestion:
        return ClarificationQuestion(
            id="context",
            prompt="Kunt u de situatie in één zin concreet maken?" if audience == "layperson"
            else "Welke feitelijke use case en welke EU-instrumenten zijn relevant?",
            options=[],
        )
