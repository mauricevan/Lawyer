"""V10.3 ILCL mode 2 — suggested legal scenarios."""
from shared.schemas.legal_clarification import ClarificationScenario


class ClarificationScenarioService:
    """Offer interpretation branches when ambiguity persists."""

    def suggest(self, question: str, audience: str = "layperson") -> list[ClarificationScenario]:
        lowered = question.lower()
        if any(h in lowered for h in ("legitim", "identif", "paspoort", "eidas", "kyc")):
            return self._identification_scenarios(audience)
        if any(h in lowered for h in ("platform", "marktplaats", "app", "advertent")):
            return self._platform_scenarios(audience)
        if any(h in lowered for h in ("webshop", "verkopen", "consument")):
            return self._commerce_scenarios(audience)
        return self._generic_scenarios(audience)

    def _identification_scenarios(self, audience: str) -> list[ClarificationScenario]:
        return [
            ClarificationScenario(
                id="A",
                label="Online account of app",
                description="U moet zich identificeren om een digitaal account te gebruiken.",
                frameworks=["eIDAS", "AVG", "sectorale KYC"],
            ),
            ClarificationScenario(
                id="B",
                label="Bank of betaling",
                description="Een financiële instelling vraagt identiteitsbewijs (KYC).",
                frameworks=["AML/KYC", "eIDAS", "betaaldiensten"],
            ),
            ClarificationScenario(
                id="C",
                label="Reizen of overheidsdienst",
                description="Identificatie voor reizen of een publieke procedure in de EU.",
                frameworks=["Schengen", "eIDAS", "digitale overheid"],
            ),
        ]

    def _platform_scenarios(self, audience: str) -> list[ClarificationScenario]:
        return [
            ClarificationScenario(
                id="A",
                label="Online marktplaats starten",
                description="Gebruikers verkopen onderling; u bent platformoperator.",
                frameworks=["DSA", "e-commerce", "consumentenrecht"],
            ),
            ClarificationScenario(
                id="B",
                label="App met advertenties",
                description="U bouwt een app met advertenties en gebruikerscontent.",
                frameworks=["DSA", "transparantieverplichtingen"],
            ),
            ClarificationScenario(
                id="C",
                label="Informatieve website",
                description="U publiceert vooral eigen content zonder intermediair platform.",
                frameworks=["e-commerce", "informatieplichten"],
            ),
        ]

    def _commerce_scenarios(self, audience: str) -> list[ClarificationScenario]:
        return [
            ClarificationScenario(
                id="A",
                label="Eigen webshop",
                description="U verkoopt zelf producten aan consumenten in de EU.",
                frameworks=["consumentenrecht", "e-commerce"],
            ),
            ClarificationScenario(
                id="B",
                label="Marktplaats voor derden",
                description="Anderen verkopen via uw platform.",
                frameworks=["DSA", "platformregels"],
            ),
            ClarificationScenario(
                id="C",
                label="B2B-only verkoop",
                description="Geen consumenten; zakelijke afnemers.",
                frameworks=["interne markt", "contractrecht"],
            ),
        ]

    def _generic_scenarios(self, audience: str) -> list[ClarificationScenario]:
        return [
            ClarificationScenario(
                id="A",
                label="Compliance-check",
                description="U wilt weten welke EU-regels op uw activiteit van toepassing zijn.",
                frameworks=["sectorale EU-wetgeving"],
            ),
            ClarificationScenario(
                id="B",
                label="Handhavingsvraag",
                description="Een toezichthouder of lidstaat legt eisen op.",
                frameworks=["handhaving", "interne markt"],
            ),
        ]
