"""Consumer-rights extractive answer templates."""
from typing import Any

from backend.src.utils.legal_chunk_text import clean_chunk_text, parse_article_number

_CELEX = "32011L0083"
_LABEL = "Richtlijn 2011/83/EU consumentenrechten"


def build_consumer_withdrawal_layperson(chunks: list[dict[str, Any]]) -> str:
    """Layperson answer for herroepingstermijn / bedenktijd."""
    excerpt = _find_article_text(chunks, "9")
    kort = (
        "De **herroepingstermijn** bij een **overeenkomst op afstand** is in principe "
        "**14 kalenderdagen** (artikel 9 Richtlijn 2011/83/EU), te rekenen vanaf de dag "
        "na ontvangst van het product."
    )
    uitleg = (
        f"Volgens {_LABEL}, artikel 9: consumenten mogen binnen 14 dagen zonder opgave "
        "van redenen van de overeenkomst afzien. Artikel 10 beschrijft hoe u herroept; "
        "artikel 22 de terugbetaling. Sommige producten zijn uitgezonderd (artikel 16)."
    )
    if excerpt:
        uitleg += f"\n\nBron: {excerpt[:320]}…"
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"## Uitleg\n{uitleg}\n\n"
        f"## Wat dit voor u kan betekenen\n"
        "Stuur binnen 14 dagen een duidelijke herroeping (bijv. e-mail). Bewaar bewijs. "
        "De verkoper moet binnen 14 dagen na herroeping terugbetalen.\n\n"
        f"## Let op\nDit is geen persoonlijk juridisch advies. Raadpleeg een jurist of "
        f"ECC Nederland bij twijfel over uitzonderingen."
    )


def build_consumer_withdrawal_professional(chunks: list[dict[str, Any]]) -> str:
    """Professional answer for herroepingstermijn."""
    excerpt = _find_article_text(chunks, "9")
    kort = (
        "De standaard **herroepingstermijn** voor **overeenkomsten op afstand** bedraagt "
        "**14 kalenderdagen** ingevolge **art. 9 Richtlijn 2011/83/EU**, te rekenen vanaf "
        "de dag na ontvangst van de goederen door de consument (tenzij art. 16 uitzondert)."
    )
    table = (
        "| Artikel | Onderwerp |\n|---|---|\n"
        "| **Art. 9** | Termijn van 14 kalenderdagen; startdatum bij goederen/diensten |\n"
        "| **Art. 10** | Uitoefening herroepingsrecht (ondubbelzinnige verklaring) |\n"
        "| **Art. 16** | Uitzonderingen op herroepingsrecht |\n"
        "| **Art. 22** | Gevolgen van herroeping (terugbetaling binnen 14 dagen) |"
    )
    quote = f"\n\n> {excerpt[:400]}…" if excerpt else ""
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"## Wettelijke grondslag\n{table}{quote}\n\n"
        f"## Bronnen\n"
        f"- CELEX {_CELEX}, Art. 9\n"
        f"- CELEX {_CELEX}, Art. 10\n"
        f"- CELEX {_CELEX}, Art. 16\n"
        f"- CELEX {_CELEX}, Art. 22\n\n"
        f"## Let op\nDit is geen juridisch advies. Verifieer op EUR-Lex."
    )


def _find_article_text(chunks: list[dict[str, Any]], article: str) -> str:
    for chunk in chunks:
        raw = str(chunk.get("text", ""))
        number = str(chunk.get("article_number") or parse_article_number(raw) or "")
        if number.lstrip("0") == article.lstrip("0"):
            return clean_chunk_text(raw)
    return ""
