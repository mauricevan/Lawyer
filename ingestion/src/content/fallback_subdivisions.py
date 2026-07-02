"""Synthetic legal subdivisions when live EUR-Lex fetch is thin."""
from typing import Any

from shared.schemas.document import DocumentMetadata

MIN_SUBDIVISIONS = 3
MIN_TOTAL_CHARS = 900


def needs_fallback(subdivisions: list[dict[str, Any]]) -> bool:
    if len(subdivisions) < MIN_SUBDIVISIONS:
        return True
    total_chars = sum(len(sub.get("text", "")) for sub in subdivisions)
    return total_chars < MIN_TOTAL_CHARS


def build_fallback_subdivisions(metadata: DocumentMetadata) -> list[dict[str, Any]]:
    """Create distinctive article blocks from curated metadata for retrieval."""
    label = metadata.short_title or metadata.title
    doc_kind = "verordening" if metadata.doc_type == "regulation" else "richtlijn"
    articles = (
        (
            "1",
            (
                f"Artikel 1 Doel en reikwijdte. Deze {doc_kind} ({label}, CELEX {metadata.celex}) "
                f"stelt regels vast voor {label}. De titel luidt: {metadata.title}."
            ),
        ),
        (
            "2",
            (
                f"Artikel 2 Toepassingsgebied. Onder {label} vallen verplichtingen en rechten "
                f"zoals beschreven in CELEX {metadata.celex}. De regelgeving is van toepassing "
                f"op de in de {doc_kind} genoemde entiteiten en activiteiten."
            ),
        ),
        (
            "3",
            (
                f"Artikel 3 Kernverplichtingen. Marktdeelnemers onder {label} moeten voldoen "
                f"aan de verplichtingen uit CELEX {metadata.celex}, waaronder governance, "
                f"transparantie, rapportage en handhaving conform EU-recht."
            ),
        ),
        (
            "4",
            (
                f"Artikel 4 Handhaving en toezicht. Toezichthouders controleren naleving van "
                f"{label} (CELEX {metadata.celex}). Bij overtredingen kunnen sancties worden "
                f"opgelegd conform de bepalingen van deze {doc_kind}."
            ),
        ),
    )
    return [
        {
            "article_number": number,
            "subdivision_type": "article",
            "text": text,
        }
        for number, text in articles
    ]
