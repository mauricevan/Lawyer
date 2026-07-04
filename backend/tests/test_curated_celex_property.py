"""Property-style tests: curated CELEX hints resolve via discovery."""
import pytest

from backend.src.services.celex_discovery_service import CelexDiscoveryService
from ingestion.src.data.curated_loader import load_curated_documents

_SAMPLE_CELEX = ("32004L0035", "32011L0083", "32016R0679", "32022R2554")


@pytest.mark.parametrize("celex", _SAMPLE_CELEX)
def test_curated_short_title_discovery(celex: str):
    document = next(doc for doc in load_curated_documents() if doc.celex == celex)
    label = document.short_title or document.title[:40]
    question = f"Wat verplicht artikel 1 van {label}?"
    hits = CelexDiscoveryService().discover_sync(question, limit=3)
    celexes = {hit.celex for hit in hits}
    assert celex in celexes
