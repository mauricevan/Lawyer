"""Chunk text cleanup for extractive legal answers."""
import re

from backend.src.utils.legal_text_trimmer import trim_legal_preamble

_CELEX_PREFIX = re.compile(
    r"^CELEX:\S+\s*\|\s*[^|]+\s*\|\s*Artikel\s+(\d+)\s*\|\s*article\s*",
    re.IGNORECASE,
)
_XML_NAME = re.compile(r"L_\d{4}[A-Z0-9_]*\.xml", re.I)
_PIPE_CELLS = re.compile(r"\|[^|\n]+")
_ARTICLE_HEAD = re.compile(r"^Artikel\s+(\d+)\s*", re.IGNORECASE)
_RECITAL_MARKERS = (
    "having regard to",
    "after transmission of the draft",
    "whereas",
    "gezien het verdrag",
    "gezien het voorstel van de commissie",
    "het europees parlement en de raad",
    "from the european commission",
    "thereof, from the",
    "in accordance with article",
    "opinion of the european economic",
    "together with the adaptation",
    "in the absence of european standards",
    "specialised committee",
    "overwegende hetgeen volgt",
    "overwegende dat",
    "gelet op het verdrag",
    "considering that",
    "failure to act could result",
)
_EUR_LEX_TITLE = re.compile(r"^EUR-Lex\s*-\s*\d{5}[A-Z]\d{4}\s*-\s*[A-Z]{2}\s*$", re.I)
_DUTCH_HINTS = (" de ", " het ", " een ", " van ", " zijn ", " worden ", " artikel ", "exploitant", "richtlijn", "verplicht")
_ENGLISH_HINTS = (" the ", " shall ", " article ", " directive ", " operator ", " member states", " whereas ")
_OPERATIVE_MARKERS = (
    "shall", "must", "required", "verplicht", "fabrikant", "manufacturer",
    "aansprakelijk", "risico", "risk", "notify", "inform", "melden",
)
_DEFINITION_QUESTION_HINTS = ("betekent", "definitie", "definition", "wat is", "what is", "wordt gedefinieerd")
_DEFINITION_CHUNK_MARKERS = ("wordt verstaan", "verstaan onder", "begripsbepaling", "begripsbepalingen")


def clean_chunk_text(text: str, focus_terms: tuple[str, ...] | None = None) -> str:
    body = text or ""
    body = _CELEX_PREFIX.sub("", body)
    body = _XML_NAME.sub("", body)
    body = re.sub(r"\|\s*section\s*\.?\s*", " ", body, flags=re.IGNORECASE)
    body = _PIPE_CELLS.sub(" ", body)
    body = trim_legal_preamble(body, focus_terms=focus_terms)
    body = re.sub(r"^\(\d+\)\s+", "", body)
    return re.sub(r"\s+", " ", body).strip()


def is_metadata_dump(text: str) -> bool:
    """True when chunk is pipe-table metadata, not operative law."""
    cleaned = clean_chunk_text(text)
    if len(cleaned) >= 80:
        lowered = cleaned.lower()
        if any(marker in lowered for marker in _OPERATIVE_MARKERS):
            return False
        if parse_article_number(cleaned) or "artikel" in lowered[:120]:
            return False
    lowered = (text or "").lower()
    if ".xml" in lowered and "|" in lowered and len(cleaned) < 80:
        return True
    if "| section" in lowered or "section ." in lowered:
        return True
    if re.match(r"^\(\d+\)\s+(together|in the absence|having regard)", lowered.strip()[:120]):
        return True
    return False


def parse_article_number(text: str) -> str | None:
    match = _ARTICLE_HEAD.search(text or "")
    return match.group(1) if match else None


def is_recital_noise(text: str) -> bool:
    """True when chunk text is enacting formula / recital, not operative articles."""
    lowered = (text or "").lower()[:600]
    if any(marker in lowered for marker in _RECITAL_MARKERS):
        if not any(marker in lowered for marker in _OPERATIVE_MARKERS):
            return True
    if re.search(r"article\s+\d+\s+thereof", lowered):
        return True
    if re.match(r"^\(\d+\)\s", (text or "").strip()):
        if not any(marker in lowered for marker in _OPERATIVE_MARKERS):
            return True
    return False


def score_chunk_relevance(text: str, question: str) -> int:
    """Higher score = more relevant operative chunk for the question."""
    lowered_q = question.lower()
    lowered_t = (text or "").lower()
    score = 0
    for word in re.findall(r"[a-zà-ÿ]{4,}", lowered_q):
        if word in lowered_t:
            score += 2 if len(word) > 6 else 1
    if any(marker in lowered_t for marker in _OPERATIVE_MARKERS):
        score += 3
    if any(hint in lowered_q for hint in _DEFINITION_QUESTION_HINTS):
        if any(marker in lowered_t for marker in _DEFINITION_CHUNK_MARKERS):
            score += 4
    if is_recital_noise(text):
        score -= 10
    if "fabrikant" in lowered_q and "fabrikant" in lowered_t:
        score += 8
    if "fabrikant" in lowered_q and "importeur" in lowered_t and "fabrikant" not in lowered_t:
        score -= 4
    if "exploitant" in lowered_q and "exploitant" in lowered_t:
        score += 8
    if "exploitant" in lowered_q and lowered_t.startswith(("de bevoegde instantie", "de lidstaat")):
        score -= 4
    if any(word in lowered_q for word in ("douane", "invoer", "import", "china", "webshop", "pakket")):
        if any(marker in lowered_t for marker in ("aangifte", "vrijmaking", "vrije verkeer", "douanewetboek")):
            score += 10
        if "artikel 156" in lowered_t or "156" in lowered_t[:40]:
            score += 6
        if "commissie gelast" in lowered_t or "krachtens lid 1 vast te stellen" in lowered_t:
            score -= 12
    if "risico" in lowered_q or "veilig" in lowered_q:
        if any(w in lowered_t for w in ("risico", "gevaar", "melden", "waarschuwen", "corrigeren")):
            score += 4
    if any(w in lowered_q for w in ("legitim", "identif", "paspoort", "identiteitskaart")):
        if any(
            marker in lowered_t
            for marker in (
                "identiteitskaart",
                "paspoort",
                "identity card",
                "passport",
                "recht van toegang",
                "right of entry",
            )
        ):
            score += 12
        if any(marker in lowered_t for marker in ("elektronische zegel", "electronic seal", "certificaat")):
            score -= 8
    return score


def is_eurlex_placeholder_title(title: str) -> bool:
    """True for generic EUR-Lex HTML titles like 'EUR-Lex - 32004L0035 - NL'."""
    return bool(_EUR_LEX_TITLE.match((title or "").strip()))


def matches_query_language(text: str, language: str) -> bool:
    """Heuristic: chunk text matches requested answer language."""
    lowered = clean_chunk_text(text).lower()
    if not lowered.strip():
        return False
    code = language.lower().split("-")[0]
    if code == "nl":
        if any(
            phrase in lowered
            for phrase in (
                "failure to act", " shall ", "the operator", "member states",
                "whereas", "considering that", "having regard",
            )
        ):
            return False
        dutch = sum(1 for hint in _DUTCH_HINTS if hint in lowered)
        english = sum(1 for hint in _ENGLISH_HINTS if hint in lowered)
        return dutch >= english or dutch >= 2
    if code == "en":
        english = sum(1 for hint in _ENGLISH_HINTS if hint in lowered)
        dutch = sum(1 for hint in _DUTCH_HINTS if hint in lowered)
        return english >= dutch or english >= 2
    return True

