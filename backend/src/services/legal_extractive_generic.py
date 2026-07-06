"""Generic extractive answers from operative EU legal chunks (no topic template)."""
import re
from typing import Any

from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.defined_term_extractor import extract_defined_term
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
    planned_norm = {a.lstrip("0") for a in planned}
    seen: set[str] = set()
    items: list[tuple[int, dict[str, str]]] = []
    defined = extract_defined_term(question).term
    for chunk in chunks:
        raw = str(chunk.get("text", "")).strip()
        focus_terms = chunk_focus_terms(chunk, question)
        cleaned = clean_chunk_text(raw, focus_terms=focus_terms)
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
        leading = parse_article_number(cleaned)
        if leading:
            article = leading
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
        rank = 0 if article in planned or article.lstrip("0") in planned_norm else 2
        if planned_norm and article.lstrip("0") in planned_norm:
            rank -= 8
        rank -= score_chunk_relevance(cleaned, question)
        rank += _platform_rank_penalty(cleaned, question)
        rank += _customs_celex_rank(str(chunk.get("celex", "")), question)
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
    lowered_q = question.lower()
    if any(word in lowered_q for word in ("douane", "invoer", "import", "china", "webshop", "pakket", "etsy")):
        customs_items = [item for _, item in items if item["celex"] == "32013R0952"]
        if customs_items:
            items = [(0, item) for item in customs_items] + [
                (rank, item) for rank, item in items if item["celex"] != "32013R0952"
            ]
    if any(word in lowered_q for word in ("terugroep", "terughaal", "recall", "onveilig")):
        recall_items = [
            item for _, item in items if "terugroep" in item["text"].lower()
        ]
        if recall_items:
            items = [(0, item) for item in recall_items] + [
                (rank, item) for rank, item in items if item not in recall_items
            ]
    if defined:
        markers = ("wordt verstaan", "verstaan onder", "begripsbepaling", "for the purposes", "shall mean")
        term_items = [
            item for _, item in items
            if _chunk_defines_term(item["text"], defined, markers)
        ]
        if term_items:
            items = [(0, item) for item in term_items] + [
                (rank, item) for rank, item in items if item not in term_items
            ]
        else:
            term_items = [
                item for _, item in items
                if _text_contains_defined_term(item["text"], defined)
            ]
            if term_items:
                items = [(0, item) for item in term_items] + [
                    (rank, item) for rank, item in items if item not in term_items
                ]
    return [item for _, item in items[:limit]]


def chunk_focus_terms(chunk: dict[str, Any], question: str) -> tuple[str, ...] | None:
    """Preserve the operative passage when trimming long definition articles."""
    defined = extract_defined_term(question).term
    if defined:
        return (defined,)
    terms: list[str] = []
    for term in chunk.get("matched_terms") or []:
        text = str(term).strip().lower()
        if len(text) >= 3:
            terms.append(text)
    unique = tuple(dict.fromkeys(terms))
    return unique or None


def _chunk_defines_term(text: str, term: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    if not _text_contains_defined_term(lowered, term):
        return False
    if any(marker in lowered for marker in markers):
        return True
    return bool(_quoted_definition_pattern(term).search(text))


def _text_contains_defined_term(text: str, term: str) -> bool:
    lowered = text.lower()
    if f'"{term}"' in lowered or f"“{term}”" in lowered or f"„{term}“" in lowered:
        return True
    return bool(re.search(rf"\b{re.escape(term)}\b", lowered))


def _quoted_definition_pattern(term: str) -> re.Pattern[str]:
    quotes = r'["\'\u201c\u201d\u201e]'
    return re.compile(rf"\d+\)\s*{quotes}{re.escape(term)}{quotes}", re.IGNORECASE)


def _customs_celex_rank(celex: str, question: str) -> int:
    lowered_q = question.lower()
    if not any(word in lowered_q for word in ("douane", "invoer", "import", "china", "webshop", "pakket")):
        return 0
    if celex == "32013R0952":
        return -6
    if celex == "32015R2446":
        return 4
    return 0


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


def _platform_rank_penalty(text: str, question: str) -> int:
    lowered_q = question.lower()
    if not any(word in lowered_q for word in ("platform", "contentwebsite", "marktplaats", "website")):
        return 0
    lowered_t = text.lower()
    penalty = 0
    if any(marker in lowered_t for marker in ("commissie gelast", "krachtens lid 1 vast te stellen")):
        penalty += 12
    if any(marker in lowered_t for marker in ("hosting", "opslag", "dienstaanbieder", "intermediary")):
        penalty -= 8
    if any(word in lowered_q for word in ("douane", "invoer", "import", "china", "webshop", "pakket")):
        if any(marker in lowered_t for marker in ("aangifte", "vrijmaking", "vrije verkeer", "douanerechten")):
            penalty -= 10
        if "commissie" in lowered_t and "artikel 116" in lowered_t:
            penalty += 15
    return penalty


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
