"""V10.3 merge clarification follow-ups into an enriched legal question."""
import re

from backend.src.utils.clarification_patterns import REFUSAL_HINTS

_SCENARIO_PICK = re.compile(r"^\s*([abc])\s*[\.\-\):]", re.IGNORECASE)
_CLARIFICATION_MARKERS = (
    "juridische verduidelijking",
    "juridisch pas precies",
    "mogelijke interpretaties",
    "mis ik nog wat context",
    "op meerdere manieren worden begrepen",
    "klik hieronder op wat het best past",
    "welke situatie beschrijft het best",
    "klik op een optie hieronder",
    "kies wat het best past",
    "uw vraag:",
    "begeleiding bij uw vraag",
)
_UNSURE_HINTS = ("niet zeker", "weet niet", "geen idee", "hmm", "hm,")


def is_clarification_content(content: str) -> bool:
    """True when assistant content is an ILCL clarification prompt."""
    lowered = content.lower()
    return any(marker in lowered for marker in _CLARIFICATION_MARKERS)


def _assistant_was_clarification(message: dict) -> bool:
    if message.get("role") != "assistant":
        return False
    meta = message.get("metadata") or {}
    if meta.get("coverage_status") == "clarify_only":
        return True
    if meta.get("verification_questions"):
        return True
    return is_clarification_content(str(message.get("content", "")))


def prior_clarification_turn(history: list[dict] | None) -> bool:
    """True when the most recent assistant turn asked for ILCL clarification."""
    if not history:
        return False
    for message in reversed(history):
        if message.get("role") == "assistant":
            return _assistant_was_clarification(message)
    return False


def user_refused_clarification(question: str) -> bool:
    lowered = question.lower().strip()
    return any(h in lowered for h in REFUSAL_HINTS)


def user_still_unsure(question: str) -> bool:
    """True when the user explicitly has not picked a concrete path yet."""
    lowered = question.lower().strip()
    return any(h in lowered for h in _UNSURE_HINTS)


def clarification_turn_count(history: list[dict] | None) -> int:
    """Count prior ILCL clarification assistant turns."""
    if not history:
        return 0
    return sum(
        1 for message in history
        if message.get("role") == "assistant" and _assistant_was_clarification(message)
    )


def is_scenario_selection(question: str) -> bool:
    """True when the user picks scenario A, B or C."""
    lowered = question.strip().lower()
    if _SCENARIO_PICK.match(lowered):
        return True
    return any(
        phrase in lowered
        for phrase in (
            "online marktplaats starten",
            "online marktplaats",
            "app met advertenties",
            "informatieve website",
        )
    )


def merge_clarification_history(question: str, history: list[dict] | None) -> str:
    """Combine original question with all clarification replies."""
    if not history:
        return question
    stripped = question.strip()
    if " — verduidelijking:" in stripped:
        return stripped[:2500]
    original = _original_user_question(history)
    if not original:
        return question
    if original.strip() == question.strip() and not _any_clarification_in_history(history):
        return question
    replies = _clarification_user_replies(history)
    if question.strip() and question.strip() not in replies and question.strip() != original.strip():
        replies.append(question.strip())
    if not replies:
        return original
    return f"{original.strip()} — verduidelijking: {'; '.join(replies)}"[:2500]


def _any_clarification_in_history(history: list[dict]) -> bool:
    return any(
        message.get("role") == "assistant" and _assistant_was_clarification(message)
        for message in history
    )


def _original_user_question(history: list[dict]) -> str:
    for message in history:
        if message.get("role") == "user":
            return str(message.get("content", "")).strip()
    return ""


def _clarification_user_replies(history: list[dict]) -> list[str]:
    replies: list[str] = []
    after_clarification = False
    for message in history:
        if message.get("role") == "assistant":
            if _assistant_was_clarification(message):
                after_clarification = True
            continue
        if after_clarification and message.get("role") == "user":
            reply = str(message.get("content", "")).strip()
            if reply and reply not in replies:
                replies.append(reply)
    return replies
