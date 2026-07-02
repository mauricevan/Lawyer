"""EUR-Lex content URL builders for multi-format fetch fallbacks."""
from ingestion.src.data.language_registry_loader import get_fetch_fallback_chain

EURLEX_CONTENT = "https://eur-lex.europa.eu/legal-content"


def build_fetch_urls(celex: str, language: str = "nl") -> list[tuple[str, str]]:
    """Return ordered (url, content_type) candidates for a CELEX document."""
    fallbacks = get_fetch_fallback_chain(language)
    urls: list[tuple[str, str]] = []
    for lang_code in fallbacks:
        urls.extend([
            (f"{EURLEX_CONTENT}/{lang_code}/TXT/HTML/?uri=CELEX:{celex}", "html"),
            (f"{EURLEX_CONTENT}/{lang_code}/TXT/XML/?uri=CELEX:{celex}", "xml"),
            (f"{EURLEX_CONTENT}/{lang_code}/ALL/?uri=CELEX:{celex}", "html"),
        ])
    return urls
