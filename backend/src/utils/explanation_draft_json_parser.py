"""Parse LLM JSON section payloads into frozen ExplanationSections."""
import json
import re
from typing import Any

from shared.schemas.legal_explanation import ExplanationSectionKey, ExplanationSections

_SECTION_KEYS = {key.value for key in ExplanationSectionKey}


def parse_sections_json(raw: str) -> ExplanationSections | None:
    """Return sections when raw is JSON object with known section keys."""
    payload = _load_json_object(raw)
    if not payload:
        return None
    sections = {key: _clean_text(payload.get(key, "")) for key in _SECTION_KEYS}
    if not any(sections.values()):
        return None
    return ExplanationSections(**sections)


def _load_json_object(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    if not text.startswith("{"):
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
