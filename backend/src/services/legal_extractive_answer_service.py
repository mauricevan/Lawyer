"""Extractive answers from retrieved legal chunks (ADR-0009 — product promise fallback)."""
import re
from typing import Any

from backend.src.services.legal_extractive_consumer import (
    build_consumer_withdrawal_layperson,
    build_consumer_withdrawal_professional,
)
from backend.src.services.legal_extractive_generic import (
    build_generic_layperson,
    build_generic_professional,
)
from backend.src.services.legal_extractive_gdpr import build_gdpr_lawful_basis_professional
from backend.src.services.legal_extractive_labels import PRACTICAL_HINTS
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.legal_chunk_text import clean_chunk_text, parse_article_number

_WEAK_LLM_MARKERS = (
    "zijn relevant voor uw vraag",
    "geen relevante documenten",
    "geen relevante eu-regels",
    ".xml",
    "| article |",
    "| body",
)


class LegalExtractiveAnswerService:
    """Build structured answers directly from chunk text when LLM is weak or unavailable."""

    def __init__(self) -> None:
        self._planner = LegalSourcePlannerService()

    def count_usable_excerpts(self, chunks: list[dict[str, Any]], question: str = "") -> int:
        excerpts = self._collect_excerpts(chunks, question, limit=3)
        return sum(1 for item in excerpts if item["article"] not in {"?", ""})

    def build_layperson_answer(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        plan = self._planner.plan(question)
        if plan and plan.plan_id == "consumer_withdrawal":
            return build_consumer_withdrawal_layperson(chunks)
        generic = build_generic_layperson(question, chunks)
        if generic:
            return generic
        excerpts = self._collect_excerpts(chunks, question, limit=2)
        if not excerpts:
            return None
        kort = self._kort_antwoord(question, excerpts[0]["text"])
        uitleg = self._uitleg_block(excerpts)
        hint = self._practical_hint(question)
        return (
            f"## Kort antwoord\n{kort}\n\n"
            f"## Uitleg\n{uitleg}\n\n"
            f"## Wat dit voor u kan betekenen\n{hint}\n\n"
            f"## Let op\nDit is geen persoonlijk juridisch advies. "
            f"Raadpleeg een gekwalificeerd jurist of bevoegde autoriteit voor uw concrete situatie."
        )

    def build_professional_answer(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        plan = self._planner.plan(question)
        if plan and plan.plan_id == "gdpr_lawful_basis" and chunks:
            return build_gdpr_lawful_basis_professional(chunks)
        if plan and plan.plan_id == "consumer_withdrawal" and chunks:
            return build_consumer_withdrawal_professional(chunks)
        generic = build_generic_professional(question, chunks)
        if generic:
            return generic
        excerpts = self._collect_excerpts(chunks, question, limit=3)
        if not excerpts:
            return None
        kort = self._kort_antwoord(question, excerpts[0]["text"])
        grondslag = "\n".join(
            f"- **Art. {item['article']}** ({item['celex']}): {item['text'][:280]}…"
            for item in excerpts
        )
        return (
            f"## Kort antwoord\n{kort}\n\n"
            f"## Juridische grondslag\n{grondslag}\n\n"
            f"## Bronnen\n"
            + "\n".join(
                f"- CELEX {item['celex']}, Art. {item['article']}" for item in excerpts
            )
            + "\n\n## Let op\nDit is geen juridisch advies. Verifieer op EUR-Lex."
        )

    @staticmethod
    def should_replace_llm_output(answer_text: str, chunks: list[dict[str, Any]]) -> bool:
        if not chunks:
            return False
        if not answer_text or not answer_text.strip():
            return True
        lowered = answer_text.lower()
        return any(marker in lowered for marker in _WEAK_LLM_MARKERS)

    def _collect_excerpts(
        self,
        chunks: list[dict[str, Any]],
        question: str,
        limit: int,
    ) -> list[dict[str, str]]:
        seen: set[str] = set()
        excerpts: list[dict[str, str]] = []
        for chunk in chunks:
            raw = str(chunk.get("text", "")).strip()
            cleaned = clean_chunk_text(raw)
            if len(cleaned) < 80:
                continue
            article = str(chunk.get("article_number") or parse_article_number(raw) or "?")
            key = f"{chunk.get('celex')}:{article}"
            if key in seen:
                continue
            seen.add(key)
            excerpts.append({
                "text": cleaned,
                "article": article,
                "celex": str(chunk.get("celex", "")),
                "regulation": self._regulation_label(chunk),
            })
        excerpts.sort(key=lambda item: self._article_rank(question, item))
        return excerpts[:limit]

    @staticmethod
    def _article_rank(question: str, item: dict[str, str]) -> tuple[int, str]:
        lowered_q = question.lower()
        text = item["text"].lower()
        article = item["article"]
        if "inwerkingtreding" in text or "publicatieblad" in text:
            return (9, article)
        if "termijn" in lowered_q:
            if article == "121" or "drie jaar" in text or "3 jaar" in text:
                return (0, article)
        if "terugbetaling" in lowered_q and article in {"116", "117", "118", "119", "120", "121"}:
            return (1, article)
        if any(word in lowered_q for word in ("rechtsgrond", "rechtsgronden", "zonder toestemming")):
            if article == "6":
                return (0, article)
            if article in {"7", "13", "14"}:
                return (1, article)
        if any(word in lowered_q for word in ("herroeping", "bedenktijd", "op afstand")):
            if article == "9":
                return (0, article)
            if article in {"10", "16", "22"}:
                return (1, article)
        return (2, article)

    def _uitleg_block(self, excerpts: list[dict[str, str]]) -> str:
        parts = [
            f"Volgens {item['regulation']}, artikel {item['article']}: {item['text'][:520]}"
            for item in excerpts
        ]
        return "\n\n".join(parts)

    @staticmethod
    def _regulation_label(chunk: dict[str, Any]) -> str:
        title = str(chunk.get("title") or "").strip()
        if title and not title.endswith(".xml") and len(title) > 8:
            return title
        celex = str(chunk.get("celex", ""))
        return regulation_label(celex)

    def _practical_hint(self, question: str) -> str:
        plan = self._planner.plan(question)
        domain = plan.legal_domain if plan else None
        if domain and domain in PRACTICAL_HINTS:
            return PRACTICAL_HINTS[domain]
        lowered = question.lower()
        if any(word in lowered for word in ("douane", "invoer", "invoerrecht")):
            return PRACTICAL_HINTS["customs"]
        if any(word in lowered for word in ("avg", "privacy", "gegevens")):
            return PRACTICAL_HINTS["privacy"]
        if any(word in lowered for word in ("webshop", "garantie", "consument")):
            return PRACTICAL_HINTS["consumer"]
        return PRACTICAL_HINTS["default"]

    def _kort_antwoord(self, question: str, body: str) -> str:
        lowered_q = question.lower()
        body_lower = body.lower()
        if "termijn" in lowered_q and ("drie jaar" in body_lower or "3 jaar" in body_lower):
            return (
                "Een verzoek tot terugbetaling moet in principe **binnen drie jaar** "
                "worden ingediend (artikel 121 Douanewetboek van de Unie)."
            )
        if "terugbetaling" in lowered_q or "te veel" in lowered_q or "teveel" in lowered_q:
            if any(word in body_lower for word in ("terugbetaling", "kwijtschelding", "te veel")):
                return (
                    "**Ja, onder voorwaarden** kan terugbetaling of kwijtschelding van te veel "
                    "betaalde invoerrechten mogelijk zijn volgens het Douanewetboek van de Unie."
                )
        if re.search(r"\b(mag|kan|moet|recht op|wordt|geldt|binnen)\b", body_lower):
            return f"Op basis van de EU-bron: {body[:220]}…"
        return f"Op basis van de gevonden EU-regelgeving: {body[:200]}…"
