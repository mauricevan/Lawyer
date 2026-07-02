"""LLM answer generation via OpenRouter (Gemma) or Anthropic Claude."""
import asyncio
import logging

import httpx

from backend.src.config import settings
from backend.src.services.citation_builder_service import CitationBuilderService
from shared.schemas.citation import Citation

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Je bent een EU-juridisch onderzoeksassistent. Antwoord ALLEEN op basis van de verstrekte context.
Citeer altijd met CELEX-nummer en artikelnummer. Geef gestructureerde antwoorden in het Nederlands.
Als de context onvoldoende is, zeg dat expliciet en benoem welke bronnen ontbreken.
Dit is geen juridisch advies."""

LAYPERSON_SYSTEM_PROMPT = """Je bent een ervaren EU-jurist die een leek uitlegt wat de regels betekenen.
Antwoord ALLEEN op basis van de verstrekte context. Gebruik begrijpelijk Nederlands (B1-niveau).
Leg juridische termen direct uit in gewone taal. Gebruik GEEN CELEX-nummers in uw antwoordtekst.
Als de context onvoldoende is, zeg dat expliciet en adviseer een echte advocaat te raadplegen.
Dit is geen persoonlijk juridisch advies.

Gebruik altijd deze markdown-structuur:

## Kort antwoord
(Eén of twee zinnen, direct antwoord op de vraag)

## Uitleg
(Begrijpelijke uitleg van de relevante regels)

## Wat dit voor u kan betekenen
(Praktische implicaties, voorwaarden, uitzonderingen)

## Let op
(Wanneer de context onvoldoende is, of wanneer een echte advocaat nodig is)"""

FOLLOW_UP_HINT = (
    "Dit is een vervolgvraag in een lopend gesprek. Houd rekening met eerdere "
    "vragen en antwoorden. Beantwoord alleen de nieuwe vraag; herhaal geen volledige "
    "disclaimers of eerder gegeven uitleg."
)

HISTORY_WINDOW = 10

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

PROFESSIONAL_MODE_HINTS = {
    "compliance": "Geef een gestructureerd ja/nee antwoord met voorwaarden.",
    "compare": "Vergelijk de artikelen systematisch in een tabelachtig formaat.",
    "updates": "Focus op recente wijzigingen en inwerkingtreding.",
    "open": "Beantwoord de vraag volledig en bondig.",
}

LAYPERSON_MODE_HINTS = {
    "compliance": (
        "Begin met ja, nee of misschien in gewone taal. Leg daarna uit onder welke voorwaarden."
    ),
    "compare": (
        "Leg het verschil uit alsof u het aan een klant vertelt, niet als vergelijkingstabel."
    ),
    "updates": (
        "Leg uit wat er recent is veranderd en wat dat praktisch betekent voor de gebruiker."
    ),
    "open": "Beantwoord de vraag volledig in begrijpelijke taal.",
}


class LlmService:
    """Generates answers with structured citations."""

    def __init__(self) -> None:
        self._citation_builder = CitationBuilderService()

    async def generate_answer(
        self,
        question: str,
        context_chunks: list[dict],
        history: list[dict] | None = None,
        query_mode: str = "open",
        audience: str = "layperson",
    ) -> tuple[str, list[Citation]]:
        context = self._build_context(context_chunks, audience)
        mode_hint = self._mode_instruction(query_mode, audience)
        messages = self._build_messages(question, context, mode_hint, history)
        system_prompt = self._system_prompt(audience)
        try:
            text = await self._call_llm(messages, system_prompt)
        except Exception as exc:
            logger.error("LLM call failed (%s): %s", settings.llm_provider, exc)
            text = self._fallback_answer(question, context_chunks, audience)
        citations = self._citation_builder.from_chunks(context_chunks)
        return text, citations

    def _system_prompt(self, audience: str) -> str:
        if audience == "professional":
            return SYSTEM_PROMPT
        return LAYPERSON_SYSTEM_PROMPT

    async def _call_llm(self, messages: list[dict], system_prompt: str) -> str:
        if settings.llm_provider == "anthropic":
            return await asyncio.to_thread(self._call_anthropic, messages, system_prompt)
        return await self._call_openrouter(messages, system_prompt)

    async def _call_openrouter(self, messages: list[dict], system_prompt: str) -> str:
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        payload = {
            "model": settings.openrouter_model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "max_tokens": 2000,
        }
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.cors_origins.split(",")[0].strip(),
            "X-Title": "EUR-Lex RAG",
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_anthropic(self, messages: list[dict], system_prompt: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    def _build_context(self, chunks: list[dict], audience: str = "layperson") -> str:
        parts = []
        for i, c in enumerate(chunks, 1):
            if audience == "professional":
                header = (
                    f"[Bron {i}] CELEX:{c.get('celex')} "
                    f"Art.{c.get('article_number', '?')}"
                )
            else:
                title = c.get("title") or "EU-regelgeving"
                article = c.get("article_number", "?")
                header = f"[Bron {i}] {title} — artikel {article}"
            parts.append(f"{header}\n{c.get('text', '')[:1500]}")
        return "\n\n".join(parts)

    def _mode_instruction(self, mode: str, audience: str = "layperson") -> str:
        hints = PROFESSIONAL_MODE_HINTS if audience == "professional" else LAYPERSON_MODE_HINTS
        return hints.get(mode, hints["open"])

    def _build_messages(
        self, question: str, context: str, mode_hint: str, history: list[dict] | None
    ) -> list[dict]:
        messages = []
        if history:
            for msg in history[-HISTORY_WINDOW:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        follow_up = f"{FOLLOW_UP_HINT}\n\n" if history else ""
        user_content = f"{follow_up}{mode_hint}\n\nContext:\n{context}\n\nVraag: {question}"
        messages.append({"role": "user", "content": user_content})
        return messages

    def _fallback_answer(
        self, question: str, chunks: list[dict], audience: str = "layperson"
    ) -> str:
        if not chunks:
            if audience == "professional":
                return "Geen relevante documenten gevonden in de geïndexeerde corpus."
            return (
                "## Kort antwoord\n"
                "Ik heb geen relevante EU-regels gevonden voor uw vraag.\n\n"
                "## Let op\n"
                "Probeer uw vraag anders te formuleren of raadpleeg een advocaat."
            )
        top = chunks[0]
        title = top.get("title", top.get("celex"))
        article = top.get("article_number", "?")
        excerpt = top.get("text", "")[:500]
        if audience == "professional":
            return (
                f"Op basis van {title}, artikel {article}: {excerpt}..."
            )
        return (
            f"## Kort antwoord\n"
            f"Op basis van {title} lijkt artikel {article} relevant voor uw vraag.\n\n"
            f"## Uitleg\n{excerpt}...\n\n"
            f"## Let op\n"
            f"Dit is een automatisch samengesteld antwoord. Raadpleeg een advocaat bij twijfel."
        )
