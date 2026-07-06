"""V10.3 ILCL mode 3 — assumption-based case enrichment."""
from backend.src.services.clarification_scenario_service import ClarificationScenarioService
from backend.src.utils.clarification_history_merge import is_scenario_selection
from backend.src.utils.clarification_patterns import (
    ACTIVITY_HINTS,
    IDENTIFICATION_HINTS,
    PLATFORM_START_HINTS,
)
from shared.schemas.legal_clarification import ClarificationScenario


class ClarificationAssumptionService:
    """Build the most probable legal case when user cannot clarify further."""

    def __init__(self) -> None:
        self._scenarios = ClarificationScenarioService()

    def build(
        self,
        question: str,
        audience: str = "layperson",
        selection: str = "",
    ) -> tuple[str, str]:
        """Return assumption narrative and enriched question for retrieval."""
        if is_scenario_selection(selection or question):
            picked = self._match_scenario(selection or question, question, audience)
            if picked:
                return self._from_scenario(question, picked)
        return self._default_assumption(question, audience)

    def _from_scenario(self, question: str, picked: ClarificationScenario) -> tuple[str, str]:
        frameworks = ", ".join(picked.frameworks)
        narrative = (
            f"Ik ga uit van: {picked.label}. "
            f"Laat me weten als dit niet klopt."
        )
        enriched = (
            f"{question.strip()} "
            f"[ILCL-scenario {picked.id}: {picked.description}; focus op {frameworks}; EU-brede toepassing.]"
        ).strip()
        return narrative, enriched[:2500]

    def _match_scenario(
        self,
        selection: str,
        question: str,
        audience: str,
    ) -> ClarificationScenario | None:
        scenarios = self._scenarios.suggest(question, audience)
        lowered = selection.lower().strip()
        letter = lowered[0] if lowered and lowered[0] in "abc" else ""
        for scenario in scenarios:
            if letter and scenario.id.lower() == letter:
                return scenario
            if scenario.label.lower() in lowered:
                return scenario
        return scenarios[0] if scenarios else None

    def _default_assumption(self, question: str, audience: str) -> tuple[str, str]:
        lowered = question.lower()
        if any(h in lowered for h in IDENTIFICATION_HINTS):
            assumption, frameworks = self._identification_assumption(lowered)
        elif any(h in lowered for h in PLATFORM_START_HINTS) or "platform" in lowered:
            assumption = (
                "een online platform in de EU waar gebruikers onderling handelen "
                "en waar ook bedrijfsadvertenties worden getoond"
            )
            frameworks = "DSA, e-commerce en eventuele vergunningplichten"
        elif any(h in lowered for h in ("webshop", "verkopen", "winkel")):
            assumption = "een online winkel die consumenten in de EU bedient"
            frameworks = "e-commerce en consumentenrecht"
        elif any(h in lowered for h in ACTIVITY_HINTS):
            assumption = "een digitale dienst gericht op EU-gebruikers"
            frameworks = "DSA en sectorale EU-regels"
        else:
            assumption = "een ondernemingsactiviteit binnen de EU interne markt"
            frameworks = "relevante EU-kaders"
        narrative = (
            f"Ik ga uit van de meest waarschijnlijke interpretatie: {assumption}. "
            f"Laat me weten als dit niet klopt."
        )
        enriched = (
            f"{question.strip()} "
            f"[ILCL-aanname: {assumption}; focus op {frameworks}; EU-brede toepassing.]"
        ).strip()
        return narrative, enriched[:2500]

    def _identification_assumption(self, lowered: str) -> tuple[str, str]:
        if any(h in lowered for h in ("bank", "betaling", "kyc")):
            return (
                "identificatie voor een bank- of betaaldienst in de EU (KYC)",
                "eIDAS, AML/KYC-richtlijnen en nationale identificatie-eisen",
            )
        if any(h in lowered for h in ("reizen", "paspoort", "reizen binnen eu")):
            return (
                "identificatie voor reizen of grensoverschrijdende diensten binnen de EU",
                "Schengen/eIDAS en vrije verkeer van personen",
            )
        if any(h in lowered for h in ("overheid", "formulier")):
            return (
                "identificatie bij een overheidsdienst of publieke procedure in de EU",
                "eIDAS, digitale overheid en nationale identificatie-eisen",
            )
        if any(h in lowered for h in ("online account", "app", "inloggen")):
            return (
                "identificatie bij het aanmaken of gebruiken van een online account in de EU",
                "eIDAS, AVG waar relevant en sectorale identificatieregels",
            )
        return (
            "identificatie of legitimatie van een natuurlijk persoon binnen de EU",
            "eIDAS, nationale identificatieregels en sectorale KYC-verplichtingen",
        )
