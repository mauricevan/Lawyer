"""Conversational copy for layperson ILCL — mirror, context, one clear follow-up."""
from backend.src.utils.clarification_patterns import (
    COMMERCE_HINTS,
    DATA_STORAGE_HINTS,
    EMPLOYMENT_HINTS,
    IDENTIFICATION_HINTS,
    PLATFORM_START_HINTS,
    PRIVACY_HINTS,
)


def detect_topic_label(question: str) -> str:
    """Plain-language topic line for the user's question."""
    lowered = question.lower()
    if any(h in lowered for h in DATA_STORAGE_HINTS):
        return "privacy en het opslaan van gegevens (AVG/GDPR)"
    if any(h in lowered for h in IDENTIFICATION_HINTS):
        return "identificatie en legitimatie in de EU"
    if any(h in lowered for h in PRIVACY_HINTS):
        return "privacy en gegevensbescherming"
    if any(h in lowered for h in PLATFORM_START_HINTS) or "platform" in lowered:
        return "online platformen en digitale diensten (o.a. DSA)"
    if any(h in lowered for h in COMMERCE_HINTS):
        return "online verkoop en consumentenrecht"
    if any(h in lowered for h in EMPLOYMENT_HINTS):
        return "werk en arbeidsrecht in de EU"
    return "EU-regels voor ondernemers, consumenten en organisaties"


def format_layperson_clarification_intro(
    question: str,
    follow_up_prompt: str,
    topic_label: str,
) -> str:
    """Build a conversational clarification message for laypersons."""
    trimmed = _trim_question(question)
    lines = [f"**Uw vraag:** {trimmed}", ""]
    if topic_label:
        lines.append(f"Dit soort vragen gaat meestal over **{topic_label}**.")
        lines.append("")
    lines.extend([
        f"**{follow_up_prompt}**",
        "",
        "Kies wat het best past — of typ het antwoord in het veld hieronder.",
    ])
    return "\n".join(lines)


def _trim_question(question: str, max_len: int = 220) -> str:
    text = " ".join(question.strip().split())
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 1].rstrip()}…"
