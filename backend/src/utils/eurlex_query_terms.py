"""Extract generic search terms for in-document EUR-Lex research."""
import re

_NL_STOPWORDS = frozenset({
    "aan", "als", "bij", "dan", "dat", "de", "den", "der", "des", "die", "dit",
    "een", "en", "er", "het", "hoe", "ik", "in", "is", "kan", "mag", "me", "mee",
    "men", "met", "mij", "moet", "naar", "niet", "nog", "of", "om", "ook", "op",
    "te", "tot", "uit", "van", "veel", "voor", "waar", "was", "wat", "wel", "wie",
    "wil", "word", "wordt", "zijn", "zo", "zou", "the", "and", "for", "are", "with",
    "this", "that", "from", "have", "has", "which", "what", "when", "where", "who",
    "welke", "welk", "waarom", "kunnen", "moeten", "staat", "staan", "vraag",
})


def build_query_terms(
    question: str,
    keywords: tuple[str, ...] | None = None,
    min_term_len: int = 3,
) -> tuple[str, ...]:
    """Build deduplicated lowercase terms for ctrl-F style document search."""
    ordered: list[str] = []
    seen: set[str] = set()

    def add(term: str) -> None:
        cleaned = term.strip().lower()
        if len(cleaned) < min_term_len or cleaned in _NL_STOPWORDS:
            return
        if cleaned in seen:
            return
        seen.add(cleaned)
        ordered.append(cleaned)

    for keyword in keywords or ():
        add(keyword)
    for token in re.findall(r"[\wÀ-ÿ-]{3,}", question.lower()):
        add(token)
    celex_match = re.search(r"\b(\d{4})[/-](\d{3,4})\b", question)
    if celex_match:
        add(celex_match.group(1))
        add(celex_match.group(2))
    return tuple(ordered)
