"""When to show gap wrappers vs standalone clear layperson answers."""
from backend.src.utils.layperson_answer_formatter import (
    is_clear_layperson_format,
    is_weak_layperson_answer,
)


def is_publishable_clear_answer(text: str | None) -> bool:
    """True when text is a complete antwoord-eerst answer suitable to show alone."""
    if not text or not text.strip():
        return False
    return is_clear_layperson_format(text) and not is_weak_layperson_answer(text)
