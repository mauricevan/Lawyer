"""Parse Official Journal citations (e.g. 2658/87, 952/2013) into CELEX identifiers."""
import re

_OJ_WITH_BODY = re.compile(
    r"(?i)(verordening|regulation|richtlijn|directive)\s*"
    r"(?:\([^)]+\)\s*)?(?:nr\.?\s*)?(\d{1,4})/(\d{2,4})\b",
)
_OJ_WITH_INSTITUTION = re.compile(
    r"(?i)(?:\(?(?:EEG|EEC|EU|EG|EGKS)\)?\s*)?(?:nr\.?\s*)?(\d{1,4})/(\d{2,4})\b",
)
_EXPLICIT_CELEX = re.compile(r"\b(\d{5}[A-Z]\d{4})\b")
_MIN_MODERN_YEAR = 1950
_MAX_MODERN_YEAR = 2099


def parse_oj_celex(question: str) -> str | None:
    """Resolve OJ number/year citations or explicit CELEX in natural-language questions."""
    explicit = _EXPLICIT_CELEX.search(question.upper())
    if explicit:
        return explicit.group(1)
    body = _OJ_WITH_BODY.search(question)
    if body:
        doc_word = body.group(1).lower()
        doc_type = "L" if doc_word in {"richtlijn", "directive"} else "R"
        return _parts_to_celex(body.group(2), body.group(3), doc_type)
    if _has_oj_context(question):
        institution = _OJ_WITH_INSTITUTION.search(question)
        if institution:
            return _parts_to_celex(institution.group(1), institution.group(2), "R")
    return None


def _parts_to_celex(first: str, second: str, doc_type: str) -> str:
    left, right = int(first), int(second)
    modern = _resolve_modern_year_parts(left, right)
    if modern is not None:
        number, year = modern
        return _celex_from_year_number(number, year, doc_type)
    if left < 100 and right >= 100:
        year_suffix, number = left, right
    elif right < 100 and left >= 100:
        number, year_suffix = left, right
    elif right < 100:
        number, year_suffix = left, right
    else:
        year_suffix, number = left, right
    return _oj_to_celex(number, year_suffix, doc_type)


def _resolve_modern_year_parts(left: int, right: int) -> tuple[int, int] | None:
    """Map modern EU citations (952/2013 or 2016/679) to (number, full_year)."""
    if _is_full_year(left) and not _is_full_year(right):
        return right, left
    if _is_full_year(right) and not _is_full_year(left):
        return left, right
    if _is_full_year(left) and _is_full_year(right):
        number, year = (right, left) if left > right else (left, right)
        return number, year
    return None


def _is_full_year(value: int) -> bool:
    return _MIN_MODERN_YEAR <= value <= _MAX_MODERN_YEAR


def _celex_from_year_number(number: int, year: int, doc_type: str) -> str:
    return f"3{year}{doc_type}{number:04d}"


def _has_oj_context(question: str) -> bool:
    lowered = question.lower()
    signals = (
        "verordening", "regulation", "richtlijn", "directive",
        "nomenclatuur", "nomenclature", "douane", "tarief", "2658/87",
    )
    return any(signal in lowered for signal in signals)


def _oj_to_celex(number: int, year_suffix: int, doc_type: str) -> str:
    year = 1900 + year_suffix if year_suffix >= 50 else 2000 + year_suffix
    return _celex_from_year_number(number, year, doc_type)
