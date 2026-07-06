"""Declarant acceptance catalog — 10 structured + 10 layperson scenarios."""
from __future__ import annotations

from dataclasses import dataclass

from backend.tests.acceptance.declarant_assertions import DeclarantExpectation


@dataclass(frozen=True)
class CatalogScenario:
    scenario_id: str
    question: str
    chip: str | None
    expectation: DeclarantExpectation


CATALOG_SCENARIOS: tuple[CatalogScenario, ...] = (
    CatalogScenario(
        "C1",
        "Ik verkoop via webshop kleine pakketjes vanuit China naar NL onder 150 euro. "
        "Moet ik douaneaangifte doen?",
        None,
        DeclarantExpectation(
            scenario_id="C1",
            required_celex=frozenset({"32013R0952"}),
            forbidden_celex=frozenset({"32011L0083"}),
            require_uncertainties=True,
            required_article_markers=frozenset({"156"}),
        ),
    ),
    CatalogScenario(
        "C2",
        "Moet ik douaneaangifte doen?",
        "import uit derde land",
        DeclarantExpectation(
            scenario_id="C2",
            required_celex=frozenset({"32013R0952", "32015R2446"}),
        ),
    ),
    CatalogScenario(
        "I1",
        "moet ik me in de eu kunnen legitimeren",
        "overheidsdienst / formulier",
        DeclarantExpectation(
            scenario_id="I1",
            required_celex=frozenset({"32004L0038", "32014R0910"}),
            forbidden_celex=frozenset({"32011L0083"}),
            require_national_boundary=True,
            require_all_celex=True,
        ),
    ),
    CatalogScenario(
        "I2",
        "moet ik me legitimeren voor online bankieren",
        "bank of betaling",
        DeclarantExpectation(
            scenario_id="I2",
            required_celex=frozenset({"32014R0910"}),
            forbidden_celex=frozenset({"32011L0083"}),
            require_national_boundary=True,
        ),
    ),
    CatalogScenario(
        "D1",
        "mag ik een platform bouwen",
        "contentwebsite",
        DeclarantExpectation(
            scenario_id="D1",
            required_celex=frozenset({"32022R2065"}),
            forbidden_celex=frozenset({"32011L0083"}),
        ),
    ),
    CatalogScenario(
        "D2",
        "Mag ik data van klanten opslaan?",
        None,
        DeclarantExpectation(
            scenario_id="D2",
            required_celex=frozenset({"32016R0679"}),
        ),
    ),
    CatalogScenario(
        "I1-followup",
        "in welke eu wetgeving staat dat",
        None,
        DeclarantExpectation(
            scenario_id="I1-followup",
            required_celex=frozenset({"32004L0038"}),
            require_national_boundary=True,
        ),
    ),
    CatalogScenario(
        "C1-routing",
        "douane webshop import china",
        None,
        DeclarantExpectation(scenario_id="C1-routing", require_adequate=False),
    ),
    CatalogScenario(
        "N3-gap",
        "xyz onbestaande eu wetgeving topic qwerty",
        None,
        DeclarantExpectation(scenario_id="N3-gap", require_adequate=False),
    ),
    CatalogScenario(
        "D1-routing",
        "dsa platform hosting verplichtingen",
        None,
        DeclarantExpectation(scenario_id="D1-routing", require_adequate=False),
    ),
)

LAYPERSON_QUESTIONS: tuple[tuple[str, DeclarantExpectation], ...] = (
    ("moet ik douaneaangifte doen voor pakketjes uit china", DeclarantExpectation(
        scenario_id="L1", required_celex=frozenset({"32013R0952", "32015R2446"}), require_adequate=False,
    )),
    ("mag ik een webshop starten zonder de dsa te lezen", DeclarantExpectation(
        scenario_id="L2", forbidden_celex=frozenset({"32011L0083"}), require_adequate=False,
    )),
    ("moet ik me in de eu kunnen legitimeren", DeclarantExpectation(
        scenario_id="L3", require_adequate=False,
    )),
    ("mag ik klantgegevens bewaren in mijn webshop", DeclarantExpectation(
        scenario_id="L4", require_adequate=False,
    )),
    ("heb ik een ce-markering nodig voor mijn product", DeclarantExpectation(
        scenario_id="L5", require_adequate=False,
    )),
    ("kan een werkgever mij ontslaan vanwege leeftijd", DeclarantExpectation(
        scenario_id="L6", require_adequate=False,
    )),
    ("mag ik cookies plaatsen zonder toestemming", DeclarantExpectation(
        scenario_id="L7", require_adequate=False,
    )),
    ("moet ik een identiteitskaart meenemen in duitsland", DeclarantExpectation(
        scenario_id="L8", required_celex=frozenset({"32004L0038"}), require_adequate=False,
    )),
    ("wat is eidas en wanneer geldt het", DeclarantExpectation(
        scenario_id="L9", required_celex=frozenset({"32014R0910"}), require_adequate=False,
    )),
    ("mag ik producten uit china verkopen in nederland", DeclarantExpectation(
        scenario_id="L10", required_celex=frozenset({"32013R0952"}), require_adequate=False,
    )),
    ("moet ik invoerrechten betalen voor een cadeau uit de vs boven 150 euro", DeclarantExpectation(
        scenario_id="L11", required_celex=frozenset({"32013R0952"}), require_adequate=False,
    )),
    ("welke eu regels gelden voor een cookiebanner op mijn website", DeclarantExpectation(
        scenario_id="L12", require_adequate=False,
    )),
    ("kan ik met mijn nederlandse zorgverzekering een behandeling in belgië laten betalen", DeclarantExpectation(
        scenario_id="L13", require_adequate=False,
    )),
    ("hoeveel weken ouderschapsverlof minimum biedt eu recht", DeclarantExpectation(
        scenario_id="L14", require_adequate=False,
    )),
    ("mag mijn bank mijn rekening zomaar sluiten volgens eu regels", DeclarantExpectation(
        scenario_id="L15", require_adequate=False,
    )),
    ("moet mijn webshop toegankelijk zijn voor blinden volgens eu regelgeving", DeclarantExpectation(
        scenario_id="L16", require_adequate=False,
    )),
    ("ik vond glasscherven in voedsel uit spanje welke eu regels beschermen consumenten", DeclarantExpectation(
        scenario_id="L17", forbidden_celex=frozenset({"32011L0083"}), require_adequate=False,
    )),
    ("kan ik van spotify naar een andere muziekdienst mijn playlists meenemen onder de avg", DeclarantExpectation(
        scenario_id="L18", required_celex=frozenset({"32016R0679"}), require_adequate=False,
    )),
    ("wat is het wettelijk minimumloon in nederland", DeclarantExpectation(
        scenario_id="L19", require_adequate=False,
    )),
    ("is dit strafbaar", DeclarantExpectation(
        scenario_id="L20", require_adequate=False,
    )),
    ("ik importeer een elektrische auto uit duitsland welke eu regels gelden", DeclarantExpectation(
        scenario_id="L21", require_adequate=False,
    )),
    ("ben ik opgelicht via een webshop in polen kan ik via eu regels geld terug", DeclarantExpectation(
        scenario_id="L22", require_adequate=False,
    )),
    ("moet een verhuurder het energielabel geven volgens eu regels", DeclarantExpectation(
        scenario_id="L23", require_adequate=False,
    )),
    ("iemand plaatste mijn gezicht in een deepfake video helpt de eu ai act", DeclarantExpectation(
        scenario_id="L24", require_adequate=False,
    )),
    ("mijn buurman filmt mij met een drone boven mijn tuin mag dat volgens eu privacy", DeclarantExpectation(
        scenario_id="L25", required_celex=frozenset({"32016R0679"}), require_adequate=False,
    )),
    ("een bedrijf gebruikt ai om sollicitaties te sorteren welke eu regels gelden", DeclarantExpectation(
        scenario_id="L26", require_adequate=False,
    )),
    ("ik kocht online een kapotte wasmachine uit duitsland hoe lang garantie eu recht", DeclarantExpectation(
        scenario_id="L27", require_adequate=False,
    )),
    ("mijn vlucht binnen europa had 5 uur vertraging heb ik recht op compensatie", DeclarantExpectation(
        scenario_id="L28", require_adequate=False,
    )),
    ("welke eu regels gelden voor plastic verpakkingen en statiegeld", DeclarantExpectation(
        scenario_id="L29", require_adequate=False,
    )),
    ("verkoopt een app crypto aan particulieren welke eu regels gelden sinds 2024", DeclarantExpectation(
        scenario_id="L30", require_adequate=False,
    )),
)
