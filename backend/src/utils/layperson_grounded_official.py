"""Render collapsible official EUR-Lex excerpts from retrieval chunks."""
from typing import Any

from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.article_chunk_filter import _normalize_article
from backend.src.utils.legal_chunk_text import (
    clean_chunk_text,
    is_metadata_dump,
    is_recital_noise,
)
from backend.src.utils.retrieval_substance import MIN_SUBSTANTIVE_CHARS

_MAX_EXCERPT_CHARS = 1200


def render_official_text_from_chunks(
    chunks: list[dict[str, Any]],
    *,
    limit: int = 3,
    articles: set[str] | None = None,
) -> str:
    """Return markdown details block with literal article text, or empty string."""
    parts = [
        "## Officiële tekst",
        "<details>",
        "<summary>Toon letterlijke tekst uit EUR-Lex (ter controle)</summary>",
        "",
    ]
    count = 0
    allowed = {_normalize_article(a) for a in articles} if articles else None
    for chunk in chunks:
        article = str(chunk.get("article_number") or "").strip()
        text = clean_chunk_text(str(chunk.get("text", "")))
        if not article or len(text) < MIN_SUBSTANTIVE_CHARS:
            continue
        if is_recital_noise(text) or is_metadata_dump(text):
            continue
        if allowed and _normalize_article(article) not in allowed:
            continue
        celex = str(chunk.get("celex") or "")
        label = regulation_label(celex) if celex else "EU-regelgeving"
        parts.append(f"**Artikel {article} ({label})**")
        parts.append("")
        parts.append(text[:_MAX_EXCERPT_CHARS].strip())
        parts.append("")
        count += 1
        if count >= limit:
            break
    if count == 0:
        return ""
    parts.append("</details>")
    return "\n".join(parts)
