"""Filter procedural or actor-irrelevant EUR-Lex chunks for evidence validation."""
from typing import Any

from backend.src.utils.legal_chunk_text import is_metadata_dump, is_recital_noise
from shared.schemas.legal_interpretation import LegalActor

_PROCEDURAL_MARKERS = (
    "inwerkingtreding", "entry into force", "publicatieblad", "official journal",
    "deze verordening is bindend", "this regulation shall be binding",
    "wijzigt richtlijn", "amends directive", "amending regulation",
    "bijlage i", "annex i", "annex ii", "bijlage ii",
    "overwegende dat", "whereas", "gezien het verdrag", "having regard to the treaty",
)
_AMENDMENT_ONLY = (
    "wordt als volgt gewijzigd", "is hereby amended", "shall be amended",
    "vervangen door", "replaced by the following",
)
_ACTOR_MARKERS: dict[LegalActor, tuple[str, ...]] = {
    "manufacturer": ("fabrikant", "producent", "manufacturer", "importeur", "importer"),
    "consumer": ("consument", "consumer", "koper", "buyer", "herroep"),
    "employee": ("werknemer", "employee", "werknemers", "arbeid", "ontslag"),
    "authority": (
        "toezichthouder", "autoriteit", "lidstaat", "markttoezicht",
        "market surveillance", "surveillance authority",
    ),
    "platform": ("platform", "intermediary", "tussenpersoon", "hosting"),
    "operator": ("exploitant", "operator", "economic operator"),
}


def is_procedural_chunk(text: str) -> bool:
    """True when chunk is entry-into-force, annex, or amendment-only text."""
    lowered = (text or "").lower()
    if is_recital_noise(text) or is_metadata_dump(text):
        return True
    if any(marker in lowered for marker in _PROCEDURAL_MARKERS):
        if not _has_operative_substance(lowered):
            return True
    if any(marker in lowered for marker in _AMENDMENT_ONLY):
        if not _has_operative_substance(lowered):
            return True
    return False


def filter_substantive_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep chunks with operative legal content."""
    return [
        chunk for chunk in chunks
        if not is_procedural_chunk(str(chunk.get("text", "")))
    ]


def chunk_supports_actor(text: str, actor: LegalActor) -> bool:
    """True when chunk text mentions the expected legal actor."""
    if actor == "unknown":
        return True
    markers = _ACTOR_MARKERS.get(actor, ())
    lowered = (text or "").lower()
    return any(marker in lowered for marker in markers)


def _has_operative_substance(lowered: str) -> bool:
    operative = (
        "shall", "must", "verplicht", "mag niet", "right", "recht",
        "fabrikant", "consument", "werknemer", "lidstaat", "markttoezicht",
    )
    return any(marker in lowered for marker in operative)
