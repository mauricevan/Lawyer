"""LLM answer generation via OpenRouter (Gemma) or Anthropic Claude."""
import asyncio
import logging

import httpx

from backend.src.config import settings
from backend.src.services.citation_builder_service import CitationBuilderService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.article_resolver import resolve_article_number
from backend.src.utils.legal_chunk_text import clean_chunk_text
from backend.src.utils.legal_text_trimmer import trim_legal_preamble
from backend.src.utils.layperson_answer_formatter import _practical_hint
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
        context_quality: str = "hoog",
        specific_intent: bool = False,
    ) -> tuple[str, list[Citation]]:
        context = self._build_context(context_chunks, audience, context_quality)
        mode_hint = self._mode_instruction(query_mode, audience, specific_intent)
        messages = self._build_messages(question, context, mode_hint, history)
        system_prompt = self._system_prompt(audience, specific_intent)
        try:
            text = await self._call_llm(messages, system_prompt)
        except Exception as exc:
            logger.error("LLM call failed (%s): %s", settings.llm_provider, exc)
            text = self._fallback_answer(question, context_chunks, audience)
        citations = self._citation_builder.from_chunks(context_chunks)
        return text, citations

    def _system_prompt(self, audience: str, specific: bool = False) -> str:
        return get_system_prompt(audience, specific=specific)

    async def _call_llm(self, messages: list[dict], system_prompt: str) -> str:
        if settings.llm_provider == "anthropic":
            return await asyncio.to_thread(self._call_anthropic, messages, system_prompt)
        return await self._call_openrouter(messages, system_prompt)

    async def _call_openrouter(self, messages: list[dict], system_prompt: str) -> str:
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        models = [settings.openrouter_model]
        if settings.openrouter_fallback_model:
            models.append(settings.openrouter_fallback_model)
        last_error: Exception | None = None
        for model in models:
            for attempt in range(settings.llm_max_retries + 1):
                try:
                    return await self._post_openrouter(messages, system_prompt, model)
                except httpx.HTTPStatusError as exc:
                    last_error = exc
                    if exc.response.status_code == 429 and attempt < settings.llm_max_retries:
                        await asyncio.sleep(settings.llm_retry_backoff_seconds * (attempt + 1))
                        continue
                    if exc.response.status_code == 429 and model != models[-1]:
                        break
                    raise
        if last_error:
            raise last_error
        raise ValueError("OpenRouter request failed")

    async def _post_openrouter(
        self,
        messages: list[dict],
        system_prompt: str,
        model: str,
    ) -> str:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "max_tokens": settings.llm_max_tokens,
            "temperature": settings.llm_temperature,
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
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    def _article_header(self, chunk: dict, index: int, audience: str) -> str:
        article = resolve_article_number(chunk)
        if audience == "professional":
            art = f"Art.{article}" if article else "Art. (onbekend)"
            return f"[Bron {index}] CELEX:{chunk.get('celex')} {art}"
        title = chunk.get("title") or "EU-regelgeving"
        suffix = f" — artikel {article}" if article else ""
        return f"[Bron {index}] {title}{suffix}"

    def _build_context(
        self,
        chunks: list[dict],
        audience: str = "layperson",
        context_quality: str = "hoog",
    ) -> str:
        quality_line = (
            f"[BRON KWALITEIT: {context_quality} — "
            "beantwoord substantiële vragen alleen bij hoog]"
        )
        parts = [quality_line]
        for i, c in enumerate(chunks, 1):
            header = self._article_header(c, i, audience)
            body = trim_legal_preamble(str(c.get("text", "")))
            parts.append(f"{header}\n{body}")
        return "\n\n".join(parts)

    def _mode_instruction(self, mode: str, audience: str = "layperson", specific: bool = False) -> str:
        if specific:
            return get_mode_hint(mode, audience, specific=True)
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
                "## Uitleg\n"
                "Formuleer uw vraag met een EU-wetnaam of onderwerp (bijv. AVG, AI Act).\n\n"
                "## Wat dit voor u kan betekenen\n"
                "Zo kan ik gerichter zoeken in EUR-Lex.\n\n"
                "## Let op\n"
                "Dit is geen persoonlijk juridisch advies."
            )
        top = chunks[0]
        title = self._display_title(top)
        excerpt = self._meaningful_excerpt(top)
        if audience == "professional":
            article = resolve_article_number(top)
            art_label = f"artikel {article}" if article else "onbekend artikel"
            return f"Op basis van {title}, {art_label}: {excerpt}"
        article = resolve_article_number(top)
        art_line = f" (artikel {article})" if article else ""
        return (
            f"## Kort antwoord\n"
            f"Volgens {title}{art_line} gelden EU-regels die op uw vraag van toepassing kunnen zijn.\n\n"
            f"## Uitleg\n{excerpt}\n\n"
            f"## Wat dit voor u kan betekenen\n"
            f"{_practical_hint(question)}\n\n"
            f"## Let op\n"
            f"Dit is geen persoonlijk juridisch advies."
        )

    @staticmethod
    def _display_title(chunk: dict) -> str:
        title = str(chunk.get("title") or "").strip()
        celex = str(chunk.get("celex") or "")
        if not title or title.endswith(".xml") or title.startswith("L_"):
            return regulation_label(celex, "de relevante EU-verordening")
        return title

    def _meaningful_excerpt(self, chunk: dict) -> str:
        body = clean_chunk_text(str(chunk.get("text", "")))
        if not body or "| article |" in body.lower() or len(body) < 40:
            body = trim_legal_preamble(str(chunk.get("text", "")))
        sentences = [part.strip() for part in body.replace("\n", " ").split(".") if len(part.strip()) > 30]
        if not sentences:
            return body[:400] or "De EU-bron bevat regels die op uw vraag van toepassing kunnen zijn."
        return ". ".join(sentences[:3]) + "."
