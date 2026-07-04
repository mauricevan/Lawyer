"""Check whether retrieved context supports customs classification questions."""
from ingestion.src.data.cn_code_parser import extract_cn_code, is_classification_question

METADATA_MARKERS = (
    "publicatieblad nr.",
    "avis juridique",
    "bijzondere uitgave",
    "eur-lex -",
    "paragraph\n",
)
OPERATIVE_MARKERS = ("artikel", "article", "hoofdstuk", "chapter", "bijlage", "annex")


def context_supports_classification(question: str, chunks: list[dict]) -> bool:
    """True when chunk text contains the CN position needed for the question."""
    if not is_classification_question(question):
        return True
    cn_code = extract_cn_code(question)
    if not cn_code:
        return True
    corpus = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
    compact = corpus.replace(" ", "").replace(".", "")
    return cn_code in corpus or cn_code in compact


def is_metadata_only_context(chunks: list[dict]) -> bool:
    """True when chunks look like EUR-Lex title/TOC pages, not operative text."""
    joined = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
    if not joined.strip():
        return True
    has_metadata = any(marker in joined for marker in METADATA_MARKERS)
    has_operative = any(marker in joined for marker in OPERATIVE_MARKERS)
    return has_metadata and not has_operative
