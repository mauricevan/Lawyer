"""Post-process layperson answers for clarity and structure."""
from typing import Any

from backend.src.utils.legal_chunk_text import clean_chunk_text, is_recital_noise
from backend.src.utils.layperson_answer_formatter import (
    ensure_layperson_sections,
    excerpt_is_usable,
    is_clear_layperson_format,
    is_weak_layperson_answer,
    replace_fallback_boilerplate,
    strip_technical_noise,
)


class LaypersonAnswerService:
    """Applies layperson formatting rules to generated answers."""

    def format(self, answer_text: str, question: str, chunks: list[dict[str, Any]]) -> str:
        if self._is_well_formed_clear(answer_text):
            return answer_text.strip()
        cleaned = strip_technical_noise(answer_text)
        cleaned = replace_fallback_boilerplate(cleaned)
        cleaned = ensure_layperson_sections(cleaned, question)
        if chunks and is_weak_layperson_answer(cleaned):
            boosted = self._boost_from_chunks(cleaned, chunks, question)
            if not is_weak_layperson_answer(boosted):
                return boosted.strip()
        return cleaned.strip()

    @staticmethod
    def _is_well_formed_clear(answer_text: str) -> bool:
        body = answer_text or ""
        if body.count("## Kort antwoord") != 1:
            return False
        if not is_clear_layperson_format(body) and "## Uitleg" not in body:
            return False
        return not is_weak_layperson_answer(body)

    def is_weak(self, answer_text: str) -> bool:
        return is_weak_layperson_answer(answer_text)

    def _boost_from_chunks(self, text: str, chunks: list[dict], question: str) -> str:
        excerpt = self._first_meaningful_excerpt(chunks)
        if not excerpt or not excerpt_is_usable(excerpt):
            return text
        kort = excerpt[:220]
        return (
            f"## Kort antwoord\n{kort}\n\n"
            f"## Wat betekent dit in de praktijk?\n"
            f"| Verplichting | Uitleg |\n| --- | --- |\n| Kernregel | {excerpt[:280]} |\n\n"
            f"## Voorbeeld\nNoteer feiten en data; zoek hulp bij de genoemde instantie als u twijfelt.\n\n"
            f"## Let op\nDit is geen persoonlijk juridisch advies."
        )

    def _first_meaningful_excerpt(self, chunks: list[dict]) -> str:
        for chunk in chunks:
            raw = str(chunk.get("text", "")).strip()
            cleaned = clean_chunk_text(raw)
            if len(cleaned) < 80 or is_recital_noise(cleaned):
                continue
            label = str(chunk.get("title") or "EU-regelgeving").strip()
            if label.endswith(".xml") or label.startswith("L_"):
                from backend.src.services.regulation_label_service import regulation_label
                label = regulation_label(str(chunk.get("celex", "")))
            article = chunk.get("article_number")
            prefix = f"{label}, artikel {article}: " if article else f"{label}: "
            return f"{prefix}{cleaned[:400]}"
        return ""
