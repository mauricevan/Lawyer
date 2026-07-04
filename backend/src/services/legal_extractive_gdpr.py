"""GDPR-specific extractive answer templates."""
from typing import Any

from backend.src.utils.legal_chunk_text import clean_chunk_text, parse_article_number

_AVG_LABEL = "Verordening (EU) 2016/679 (AVG / GDPR)"
_CELEX = "32016R0679"

_BASIS_ROWS = (
    ("6(1)(a)", "Toestemming", "Vrijgegeven, specifieke, geïnformeerde en ondubbelzinnige wil; zie ook art. 7."),
    ("6(1)(b)", "Overeenkomst", "Verwerking noodzakelijk voor uitvoering overeenkomst of precontractuele maatregelen."),
    ("6(1)(c)", "Wettelijke verplichting", "Verwerking noodzakelijk om wettelijke verplichting na te komen."),
    ("6(1)(d)", "Vitaal belang", "Verwerking noodzakelijk om vitaal belang van betrokkene of ander natuurlijk persoon te beschermen."),
    ("6(1)(e)", "Algemeen belang / openbaar gezag", "Verwerking noodzakelijk voor taak van algemeen belang of uitoefening openbaar gezag."),
    ("6(1)(f)", "Gerechtvaardigd belang", "Noodzakelijk voor gerechtvaardigde belangen, tenzij belangen/rechten betrokkene zwaarder wegen."),
)


def build_gdpr_lawful_basis_professional(chunks: list[dict[str, Any]]) -> str:
    """Structured professional answer for AVG art. 6 rechtsgronden."""
    art6 = _find_article_text(chunks, "6")
    kort = (
        "Verwerking **zonder toestemming** kan rechtmatig zijn wanneer een **andere rechtsgrond** "
        "uit **artikel 6 lid 1 AVG** van toepassing is (sub b–f). Toestemming is één van zes grondslagen (sub a); "
        "per grondslag gelden eigen voorwaarden. Verwijs naar **art. 6**, **art. 7** (toestemming) "
        "en **art. 13–14** (informatieplicht)."
    )
    table = "| Grondslag | Omschrijving | Kernvoorwaarde |\n|---|---|---|\n"
    table += "\n".join(
        f"| **Art. {ref}** | {title} | {note} |" for ref, title, note in _BASIS_ROWS
    )
    excerpt = f"\n\n> {art6[:400]}…" if art6 else ""
    grondslag = (
        f"## Wettelijke grondslag\n{table}{excerpt}\n\n"
        f"**Aanvullend:** art. 7 AVG (voorwaarden toestemming); art. 13–14 AVG (transparantie)."
    )
    bronnen = (
        f"- CELEX {_CELEX}, Art. 6 (rechtmatigheid)\n"
        f"- CELEX {_CELEX}, Art. 7 (toestemming)\n"
        f"- CELEX {_CELEX}, Art. 13–14 (informatieplicht)"
    )
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"{grondslag}\n\n"
        f"## Bronnen\n{bronnen}\n\n"
        f"## Let op\nDit is geen juridisch advies. Verifieer op EUR-Lex."
    )


def _find_article_text(chunks: list[dict[str, Any]], article: str) -> str:
    for chunk in chunks:
        raw = str(chunk.get("text", ""))
        number = str(chunk.get("article_number") or parse_article_number(raw) or "")
        if number.lstrip("0") == article.lstrip("0"):
            return clean_chunk_text(raw)
    return ""
