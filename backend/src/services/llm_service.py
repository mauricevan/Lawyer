"""LLM answer generation via OpenRouter (Gemma) or Anthropic Claude."""
import asyncio
import logging

import httpx

from backend.src.config import settings
from backend.src.services.citation_builder_service import CitationBuilderService
from shared.config.prompt_loader import (
    get_follow_up_hint,
    get_history_window,
    get_mode_hint,
    get_system_prompt,
    load_prompt_config,
)
from shared.schemas.citation import Citation

logger = logging.getLogger(__name__)

_config = load_prompt_config()
SYSTEM_PROMPT = get_system_prompt("professional")
LAYPERSON_SYSTEM_PROMPT = get_system_prompt("layperson")
FOLLOW_UP_HINT = get_follow_up_hint()
HISTORY_WINDOW = get_history_window()
PROFESSIONAL_MODE_HINTS = _config["mode_hints"]["professional"]
LAYPERSON_MODE_HINTS = _config["mode_hints"]["layperson"]

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


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
        return get_system_prompt(audience)

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
        return get_mode_hint(mode, audience)

    def _build_messages(
        self, question: str, context: str, mode_hint: str, history: list[dict] | None
    ) -> list[dict]:
        messages = []
        if history:
            for msg in history[-get_history_window() :]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        follow_up = f"{get_follow_up_hint()}\n\n" if history else ""
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
