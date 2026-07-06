"""In-document keyword search over parsed EUR-Lex article bodies."""
from dataclasses import dataclass

from shared.schemas.eurlex_document import EurlexArticle, EurlexDocumentSession


@dataclass(frozen=True)
class ArticleSearchHit:
    """Ranked article match inside a live document session."""

    celex: str
    article_number: str
    title: str
    text: str
    score: float
    matched_terms: tuple[str, ...]


def search_articles_in_document(
    session: EurlexDocumentSession,
    query_terms: tuple[str, ...],
    *,
    article_hints: tuple[str, ...] | None = None,
    limit: int = 12,
) -> list[ArticleSearchHit]:
    """Score articles by keyword overlap — generic ctrl-F over parsed bodies."""
    if not session.articles or not query_terms:
        return _hint_only_hits(session, article_hints, limit)
    hint_set = _normalize_hints(article_hints)
    hits: list[ArticleSearchHit] = []
    for number, article in session.articles.items():
        score, matched = _score_article(article, query_terms, number in hint_set)
        if score <= 0 and number not in hint_set:
            continue
        if number in hint_set and score <= 0:
            score = 0.5
            matched = ()
        hits.append(
            ArticleSearchHit(
                celex=session.celex,
                article_number=number,
                title=article.title or session.title,
                text=article.text,
                score=score,
                matched_terms=matched,
            ),
        )
    hits.sort(key=lambda hit: (-hit.score, _article_sort_key(hit.article_number)))
    return hits[:limit]


def _score_article(
    article: EurlexArticle,
    query_terms: tuple[str, ...],
    hinted: bool,
) -> tuple[float, tuple[str, ...]]:
    haystack = f"{article.title} {article.text}".lower()
    matched: list[str] = []
    score = 0.0
    for term in query_terms:
        if term in haystack:
            matched.append(term)
            score += 2.0 if len(term) > 6 else 1.0
    if hinted:
        score += 3.0
    return score, tuple(matched)


def _hint_only_hits(
    session: EurlexDocumentSession,
    article_hints: tuple[str, ...] | None,
    limit: int,
) -> list[ArticleSearchHit]:
    if not article_hints:
        return []
    hint_set = _normalize_hints(article_hints)
    hits: list[ArticleSearchHit] = []
    for number in hint_set:
        article = session.articles.get(number)
        if not article:
            continue
        hits.append(
            ArticleSearchHit(
                celex=session.celex,
                article_number=number,
                title=article.title or session.title,
                text=article.text,
                score=1.0,
                matched_terms=(),
            ),
        )
    return hits[:limit]


def _normalize_hints(article_hints: tuple[str, ...] | None) -> set[str]:
    if not article_hints:
        return set()
    return {hint.lstrip("0") or "0" for hint in article_hints}


def _article_sort_key(number: str) -> tuple[int, str]:
    digits = "".join(ch for ch in number if ch.isdigit())
    return (int(digits) if digits else 9999, number)
