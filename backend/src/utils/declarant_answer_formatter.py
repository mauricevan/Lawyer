"""Compact declarant answer — verified EUR-Lex text with regulation and article."""
from typing import Any

from backend.src.services.legal_extractive_generic import collect_generic_excerpts
from backend.src.utils.layperson_prose_builder import _build_kort_antwoord, _extract_sentences


def build_declarant_verified_answer(
    question: str,
    chunks: list[dict[str, Any]],
) -> str | None:
    """Return markdown: kort antwoord + «De wet zegt» with article and regulation."""
    excerpts = collect_generic_excerpts(chunks, question, limit=2)
    if not excerpts:
        return None
    kort = _build_kort_antwoord(question, excerpts)
    if not kort:
        kort = (
            "In principe mag u in de EU een online platform starten, "
            "mits u aan de toepasselijke EU-regels voldoet."
        )
    law_blocks = _law_says_blocks(excerpts)
    if not law_blocks:
        return None
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"## De wet zegt\n\n"
        + "\n\n".join(law_blocks)
    )


def _law_says_blocks(excerpts: list[dict[str, str]]) -> list[str]:
    blocks: list[str] = []
    for item in excerpts[:2]:
        article = str(item.get("article", "")).strip()
        regulation = str(item.get("regulation") or item.get("celex") or "EU-regelgeving")
        sentences = _extract_sentences(str(item.get("text", "")), max_count=3)
        if not sentences:
            continue
        quote = " ".join(sentences)
        label = f"Artikel {article} ({regulation})" if article else regulation
        blocks.append(f"**{label}**\n\n«{quote}»")
    return blocks
