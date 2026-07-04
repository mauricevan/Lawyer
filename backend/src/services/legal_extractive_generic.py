"""Generic extractive answers from operative EU legal chunks (no topic template)."""
import re
from typing import Any

from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.article_resolver import resolve_article_number
from backend.src.utils.legal_chunk_text import (
    clean_chunk_text,
    is_eurlex_placeholder_title,
    is_metadata_dump,
    is_recital_noise,
    parse_article_number,
    score_chunk_relevance,
)
from backend.src.utils.layperson_prose_builder import build_layperson_sections

_GAP_MARKERS = (
    "kon geen specifieke wettekst",
    "geen betrouwbaar antwoord",
    "onvoldoende eur-lex-context",
)
_OBLIGATION_MARKERS = (
    "shall", "must", "required", "verplicht", "aansprakelijk",
    "veroorzaken", "herstellen", "voorkomen", "liable", "liability",
)


def can_build_generic_answer(chunks: list[dict[str, Any]], question: str = "") -> bool:
    """True when chunks contain enough operative legal text for extractive answer."""
    return len(collect_generic_excerpts(chunks, question, limit=1)) >= 1


def build_generic_layperson(question: str, chunks: list[dict[str, Any]]) -> str | None:
    excerpts = collect_generic_excerpts(chunks, question, limit=3)
    if not excerpts:
        return None
    prose = build_layperson_sections(question, excerpts)
    if prose:
        return prose
    return None


def build_generic_professional(question: str, chunks: list[dict[str, Any]]) -> str | None:
    excerpts = collect_generic_excerpts(chunks, question, limit=3)
    if not excerpts:
        return None
    kort = _summarize_kort(question, excerpts[0]["text"])
    rows = "\n".join(
        f"- **Art. {item['article']}** ({item['celex']}): {item['text'][:300]}…"
        for item in excerpts
    )
    bronnen = "\n".join(
        f"- CELEX {item['celex']}, Art. {item['article']}" for item in excerpts
    )
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"## Wettelijke grondslag\n{rows}\n\n"
        f"## Bronnen\n{bronnen}\n\n"
        f"## Let op\nDit is geen juridisch advies. Verifieer op EUR-Lex."
    )


def build_discovery_answer(question: str, celex: str, title: str, chunks: list[dict[str, Any]]) -> str:
    """Answer 'which directive/regulation' questions from discovery + chunks."""
    excerpts = collect_generic_excerpts(chunks, question, limit=2)
    obligation = excerpts[0]["text"][:320] if excerpts else "Zie de volledige tekst op EUR-Lex."
    return (
        f"## Kort antwoord\n"
        f"Dit valt onder **{title}** (CELEX {celex}).\n\n"
        f"## Kernverplichting\n{obligation}…\n\n"
        f"## Bronnen\n- CELEX {celex}\n\n"
        f"## Let op\nDit is geen juridisch advies. Verifieer op EUR-Lex."
    )


def is_gap_like_answer(answer_text: str) -> bool:
    lowered = (answer_text or "").lower()
    return any(marker in lowered for marker in _GAP_MARKERS)


def collect_generic_excerpts(
    chunks: list[dict[str, Any]],
    question: str,
    limit: int,
) -> list[dict[str, str]]:
    planner = LegalSourcePlannerService()
    plan = planner.plan(question)
    planned = set(plan.articles) if plan and plan.articles else set()
    seen: set[str] = set()
    items: list[tuple[int, dict[str, str]]] = []
    for chunk in chunks:
        raw = str(chunk.get("text", "")).strip()
        cleaned = clean_chunk_text(raw)
        if (
            len(cleaned) < 80
            or _is_preamble_noise(cleaned)
            or is_recital_noise(cleaned)
            or is_metadata_dump(cleaned)
            or is_metadata_dump(raw)
        ):
            continue
        article = str(
            chunk.get("article_number") or resolve_article_number(chunk) or parse_article_number(raw) or ""
        ).strip()
        if not article or article in {"?", "—", "-"}:
            if not _has_obligation_text(cleaned):
                continue
            article = parse_article_number(cleaned) or "algemeen"
        if not article:
            continue
        key = f"{chunk.get('celex')}:{article}:{cleaned[:60]}"
        if key in seen:
            continue
        seen.add(key)
        rank = 0 if article in planned or article.lstrip("0") in {a.lstrip("0") for a in planned} else 2
        rank -= score_chunk_relevance(cleaned, question)
        if planned and article.lstrip("0") not in {a.lstrip("0") for a in planned}:
            rank += 5
        items.append((rank, {
            "text": cleaned,
            "article": article,
            "celex": str(chunk.get("celex", "")),
            "regulation": _label(chunk),
        }))
    items.sort(key=lambda pair: (pair[0], pair[1]["article"]))
    if "fabrikant" in question.lower():
        manufacturer_items = [
            item for _, item in items if _chunk_about_manufacturer(item["text"])
        ]
        if manufacturer_items:
            items = [(0, item) for item in manufacturer_items]
    if "exploitant" in question.lower():
        operator_items = [item for _, item in items if _chunk_about_operator(item["text"])]
        if operator_items:
            items = [(0, item) for item in operator_items]
    return [item for _, item in items[:limit]]


def _chunk_about_manufacturer(text: str) -> bool:
    lowered = text.lower()
    if "fabrikant" not in lowered:
        return False
    if lowered.startswith(("een gemachtigde", "de gemachtigde", "het mandaat")):
        return False
    return "fabrikanten" in lowered or lowered.index("fabrikant") < 120


def _chunk_about_operator(text: str) -> bool:
    lowered = text.lower()
    if "exploitant" not in lowered:
        return False
    if lowered.startswith(("de bevoegde instantie", "de lidstaat", "lidstaten")):
        return False
    return "exploitanten" in lowered or "exploitant" in lowered[:160]


def _has_obligation_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _OBLIGATION_MARKERS)


def _is_preamble_noise(text: str) -> bool:
    lowered = text.lower()
    noise = (
        "gezien het verdrag",
        "having regard to the treaty",
        "gezien het voorstel van de commissie",
        "het europees parlement en de raad",
    )
    return any(marker in lowered for marker in noise) and "artikel" not in lowered[:120]


def _label(chunk: dict[str, Any]) -> str:
    title = str(chunk.get("title") or "").strip()
    celex = str(chunk.get("celex", ""))
    if title and not is_eurlex_placeholder_title(title) and not title.endswith(".xml") and len(title) > 8:
        return title
    return regulation_label(celex)


def _summarize_kort(question: str, body: str) -> str:
    if is_recital_noise(body):
        return "De EU-bron bevat verplichtingen voor fabrikanten bij een veiligheidsrisico."
    lead = body[:280].strip()
    if lead.endswith("…") or lead.endswith("..."):
        return f"Op basis van de EU-bron: {lead}"
    return f"Op basis van de EU-bron: {lead}…"
