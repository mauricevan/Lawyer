"""Input guardrails for query safety checks."""
import logging
import re

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

INJECTION_PATTERNS = (
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"you are now",
    r"jailbreak",
    r"<\s*script",
)
MAX_QUESTION_LENGTH = 2000


class GuardrailsService:
    """Detects suspicious prompt-injection patterns."""

    def check_question(self, question: str) -> list[str]:
        lowered = question.lower()
        hits = [
            pattern
            for pattern in INJECTION_PATTERNS
            if re.search(pattern, lowered)
        ]
        if hits:
            logger.warning("Prompt injection pattern detected: %s", hits)
        return hits

    def enforce_question(self, question: str) -> None:
        if len(question) > MAX_QUESTION_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "QUESTION_TOO_LONG",
                    "message": f"Question exceeds {MAX_QUESTION_LENGTH} characters.",
                },
            )
        hits = self.check_question(question)
        if hits:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "PROMPT_INJECTION_DETECTED",
                    "message": "Suspicious input pattern detected.",
                },
            )
