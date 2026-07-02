"""Lightweight rule-based language detection for legal queries."""
import re

_STOPWORDS: dict[str, frozenset[str]] = {
    "nl": frozenset({
        "wat", "welke", "hoe", "waar", "wanneer", "wie", "waarom",
        "onder", "volgens", "geldt", "regelt", "verplichtingen", "artikel",
        "richtlijn", "verordening", "besluit", "niet", "voor", "van", "het", "een",
    }),
    "fr": frozenset({
        "que", "quel", "quelle", "quelles", "comment", "pourquoi", "quand",
        "selon", "obligations", "règlement", "directive", "article", "les", "des",
        "une", "est", "sont", "dans", "pour", "sur",
    }),
    "de": frozenset({
        "was", "welche", "welcher", "wie", "warum", "wann", "wer", "wo",
        "nach", "verordnung", "richtlinie", "artikel", "pflichten", "gilt",
        "der", "die", "das", "ein", "eine", "und", "nicht", "für", "von",
    }),
    "es": frozenset({
        "qué", "que", "cuál", "cuáles", "cómo", "por", "cuándo", "quién",
        "según", "obligaciones", "reglamento", "directiva", "artículo", "los",
        "las", "una", "del", "para", "sobre", "está", "son",
    }),
    "en": frozenset({
        "what", "which", "how", "when", "where", "who", "why",
        "under", "according", "regulation", "directive", "article", "obligations",
        "the", "and", "for", "not", "does", "apply",
    }),
}

_TOKEN_RE = re.compile(r"[a-zàâäéèêëïîôùûüÿçñáíóúß]{3,}", re.IGNORECASE)


class LanguageDetectionService:
    """Scores stopword overlap to infer query language."""

    def detect(self, text: str) -> str:
        tokens = _TOKEN_RE.findall(text.lower())
        if not tokens:
            return "nl"
        scores = {
            lang: sum(1 for token in tokens if token in words)
            for lang, words in _STOPWORDS.items()
        }
        best_lang = max(scores, key=scores.get)
        return best_lang if scores[best_lang] > 0 else "nl"
