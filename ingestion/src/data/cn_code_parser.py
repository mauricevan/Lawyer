"""Detect CN/TARIC classification questions and extract goods codes."""
import re

from shared.config.cn_classification_loader import get_classification_signals, get_import_signals

_CN_CODE = re.compile(r"\b(\d{4})(?:[\s.]?(\d{2}))?(?:[\s.]?(\d{2}))?\b")


def extract_cn_code(question: str) -> str | None:
    """Return the 4-digit CN position when a goods code appears in the question."""
    for match in _CN_CODE.finditer(question):
        position = match.group(1)
        if position.startswith(("19", "20")) and len(question) > 40:
            continue
        return position
    return None


def extract_cn_code_full(question: str) -> str | None:
    """Return normalized CN code up to 8 digits (e.g. 01012100)."""
    match = _CN_CODE.search(question)
    if not match:
        return None
    parts = [match.group(1), match.group(2), match.group(3)]
    return "".join(part for part in parts if part)


def is_classification_question(question: str) -> bool:
    """True when the user asks about customs goods-code classification."""
    lowered = question.lower()
    has_code = extract_cn_code(question) is not None
    if not has_code:
        return False
    has_class_signal = any(signal in lowered for signal in get_classification_signals())
    has_import_signal = any(signal in lowered for signal in get_import_signals())
    has_quality_check = any(
        phrase in lowered
        for phrase in ("juist", "klopt", "goed", "kans", "correct", "classific")
    )
    return has_class_signal or has_import_signal or has_quality_check
