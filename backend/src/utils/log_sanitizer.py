"""Redact sensitive values from log messages."""
import re

REDACTION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"sk-or-v1-[A-Za-z0-9_-]+"), "sk-or-v1-[REDACTED]"),
    (re.compile(r"sk-ant-[A-Za-z0-9_-]+"), "sk-ant-[REDACTED]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]+"), "Bearer [REDACTED]"),
    (re.compile(r"(password=)[^&\s]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(api_key=)[^&\s]+", re.I), r"\1[REDACTED]"),
)


def sanitize_log_message(message: str) -> str:
    """Return message with known secret patterns redacted."""
    output = message
    for pattern, replacement in REDACTION_RULES:
        output = pattern.sub(replacement, output)
    return output
