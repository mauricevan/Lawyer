"""Build LLM context from retrieval chunks only — no planner templates."""
from typing import Any

from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.legal_chunk_text import clean_chunk_text
from backend.src.utils.retrieval_substance import MIN_SUBSTANTIVE_CHARS

_MAX_CONTEXT_CHARS = 6000


def build_grounded_context(chunks: list[dict[str, Any]]) -> str:
    """Return EUR-Lex article text blocks for grounded answer generation."""
    blocks: list[str] = []
    total = 0
    for chunk in chunks[:8]:
        article = str(chunk.get("article_number") or "").strip()
        text = clean_chunk_text(str(chunk.get("text", "")))
        if not article or len(text) < MIN_SUBSTANTIVE_CHARS:
            continue
        celex = str(chunk.get("celex") or "")
        label = regulation_label(celex) if celex else "EU-regelgeving"
        block = f"[{label}, artikel {article}]\n{text[:1200]}"
        if total + len(block) > _MAX_CONTEXT_CHARS:
            break
        blocks.append(block)
        total += len(block)
    return "\n\n---\n\n".join(blocks)
