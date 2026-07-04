"""Environmental liability question resolves to CELEX 32004L0035."""
from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.services.legal_extractive_generic import build_generic_professional
from backend.src.utils.celex_hint_resolver import resolve_live_celex_hint

ENV_QUESTION = (
    "Welke verplichtingen legt de Europese Milieuaansprakelijkheidsrichtlijn "
    "op aan exploitanten die milieuschade veroorzaken?"
)

CHUNKS = [{
    "celex": "32004L0035",
    "title": "Richtlijn 2004/35/EG milieuaansprakelijkheid",
    "article_number": "4",
    "text": (
        "Artikel 4. De exploitant is verplicht onmiddellijk de nodige maatregelen te nemen "
        "om milieuschade te voorkomen of te beheersen en om de schade te herstellen."
    ) * 3,
}]


def test_environmental_liability_celex_discovery():
    assert CelexDiscoveryService().high_confidence_celex(ENV_QUESTION) == "32004L0035"


def test_environmental_liability_live_hint():
    assert resolve_live_celex_hint(ENV_QUESTION, None, None) == "32004L0035"


def test_environmental_liability_extractive_answer():
    answer = build_generic_professional(ENV_QUESTION, CHUNKS)
    assert answer is not None
    assert "32004L0035" in answer
    assert "verplicht" in answer.lower() or "milieuschade" in answer.lower()
