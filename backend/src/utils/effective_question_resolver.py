"""Resolve merged dossier question — single source of truth for ILCL and retrieval."""
from backend.src.utils.clarification_history_merge import (
    merge_clarification_history,
    prior_clarification_turn,
)


def resolve_effective_question(raw_question: str, history: list[dict] | None) -> str:
    """Return merged dossier text; never drop prior turns when clarifying."""
    if not history:
        return raw_question.strip()
    if prior_clarification_turn(history) or _has_prior_user_turn(history):
        return merge_clarification_history(raw_question, history)
    return raw_question.strip()


def _has_prior_user_turn(history: list[dict]) -> bool:
    users = [m for m in history if m.get("role") == "user"]
    return len(users) >= 1
