"""Normalize EU legal titles and questions for CELEX discovery matching."""
import re

_STOPWORDS = frozenset({
    "welke", "welk", "wat", "hoe", "waar", "wie", "wanneer", "waarom",
    "legt", "leggen", "op", "aan", "van", "voor", "bij", "met", "zonder",
    "de", "het", "een", "die", "dat", "dit", "deze", "der", "den", "des",
    "in", "en", "of", "als", "kan", "mag", "moet", "wordt", "worden",
    "volgens", "onder", "over", "naar", "uit", "door", "te", "om",
    "the", "and", "for", "with", "from", "that", "this", "which",
    "richtlijn", "verordening", "besluit", "directive", "regulation",
})

_SUFFIX_PATTERN = re.compile(
    r"\b(-?\s*richtlijn|-?\s*verordening|-?\s*directive|-?\s*regulation)\b",
    re.IGNORECASE,
)


def normalize_question_for_discovery(text: str) -> str:
    """Lowercase, strip suffixes, remove stopwords, collapse whitespace."""
    lowered = text.lower().strip()
    lowered = _SUFFIX_PATTERN.sub(" ", lowered)
    lowered = re.sub(r"[^\w\sà-ÿ-]", " ", lowered)
    tokens = [token for token in lowered.split() if token and token not in _STOPWORDS]
    return " ".join(tokens)


def normalize_title_label(title: str) -> str:
    """Normalize a document title for index lookup."""
    cleaned = re.sub(r"\([^)]*\)", "", title).strip().lower()
    cleaned = _SUFFIX_PATTERN.sub(" ", cleaned)
    for prefix in ("verordening ", "richtlijn ", "besluit ", "directive ", "regulation "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize_meaningful(text: str) -> list[str]:
    """Return tokens with length >= 3 after normalization."""
    normalized = normalize_question_for_discovery(text)
    return [token for token in normalized.split() if len(token) >= 3]


def score_title_overlap(query_tokens: list[str], title: str) -> float:
    """Token overlap score in [0, 1] with word-boundary bonus for long terms."""
    if not query_tokens or not title:
        return 0.0
    title_norm = normalize_title_label(title)
    title_tokens = set(tokenize_meaningful(title_norm))
    if not title_tokens:
        return 0.0
    hits = sum(1 for token in query_tokens if token in title_tokens)
    overlap = hits / max(len(query_tokens), 1)
    joined = " ".join(query_tokens)
    if len(joined) >= 8 and joined in title_norm:
        overlap = max(overlap, 0.92)
    elif any(
        len(token) >= 10 and _token_matches_title_word(token, title_norm)
        for token in query_tokens
    ):
        overlap = max(overlap, 0.85)
    return min(1.0, overlap)


def _token_matches_title_word(token: str, title_norm: str) -> bool:
    """Match whole-word tokens only — avoids gezondheid → gezondheidsgegevens."""
    return bool(re.search(rf"\b{re.escape(token)}\b", title_norm))
