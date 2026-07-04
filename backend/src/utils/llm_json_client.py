"""Call LLM and parse JSON responses for structured agent steps."""
import json
import logging
import re

import httpx

from backend.src.config import settings

logger = logging.getLogger(__name__)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
_JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


async def call_llm_json(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> dict:
    """Return parsed JSON object from LLM response."""
    text = await _call_llm_text(system_prompt, user_prompt, max_tokens)
    return _parse_json_object(text)


def _parse_json_object(text: str) -> dict:
    stripped = text.strip()
    block = _JSON_BLOCK.search(stripped)
    if block:
        stripped = block.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object in LLM response")
    return json.loads(stripped[start : end + 1])


async def _call_llm_text(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    if settings.llm_provider == "anthropic":
        return await _call_anthropic(system_prompt, user_prompt, max_tokens)
    return await _call_openrouter(system_prompt, user_prompt, max_tokens)


async def _call_openrouter(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured")
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def _call_anthropic(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
