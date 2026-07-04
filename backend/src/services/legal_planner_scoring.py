"""Score explicit legal source plans — best match wins (ADR-0009 maturity)."""
import re
from typing import Any

from backend.src.utils.legal_domain_retrieval_filter import is_celex_allowed_for_domain


def score_explicit_plan(
    lowered_question: str,
    entry: dict[str, Any],
    discovery_celexes: frozenset[str] | None = None,
    legal_issue: str | None = None,
    routing_domain: str | None = None,
) -> int:
    """Return match score; 0 means no match."""
    celex = str(entry.get("celex", ""))
    if routing_domain and routing_domain != "unknown":
        if not is_celex_allowed_for_domain(celex, routing_domain):  # type: ignore[arg-type]
            return 0
    triggers = entry.get("triggers_any", [])
    if not triggers:
        return 0
    score = 0
    matched = 0
    for trigger in triggers:
        if not _trigger_matches(lowered_question, str(trigger)):
            continue
        matched += 1
        token = str(trigger)
        weight = len(token) + (12 if len(token) >= 12 else 0) + (8 if " " in token else 0)
        score += weight
    if matched == 0:
        return 0
    score += _celex_bonus(lowered_question, celex)
    score += _directive_number_bonus(lowered_question, celex)
    score += _issue_fit_bonus(entry, legal_issue)
    score += _routing_domain_bonus(entry, routing_domain)
    if discovery_celexes and celex in discovery_celexes:
        score += 45
    return score


def _routing_domain_bonus(entry: dict[str, Any], routing_domain: str | None) -> int:
    if not routing_domain or routing_domain == "unknown":
        return 0
    yaml_domain = str(entry.get("legal_domain", ""))
    mapping = {
        "employment_law": "employment",
        "consumer_protection": "consumer",
        "product_safety": "consumer",
        "administrative_law": "consumer",
        "data_protection": "privacy",
        "digital_services": "digital",
        "internal_market": "internal_market",
    }
    expected = mapping.get(routing_domain)
    if expected and yaml_domain == expected:
        return 20
    return 0


def _issue_fit_bonus(entry: dict[str, Any], legal_issue: str | None) -> int:
    """Penalize plans whose issue_fit conflicts with interpreted question issue."""
    if not legal_issue or legal_issue == "unknown":
        return 0
    fit = entry.get("issue_fit") or []
    if not fit:
        return 0
    if legal_issue in fit:
        return 15
    return -40


def pick_best_explicit_plan(
    lowered_question: str,
    plans: list[dict[str, Any]],
    min_score: int = 10,
    discovery_celexes: frozenset[str] | None = None,
    legal_issue: str | None = None,
    routing_domain: str | None = None,
) -> dict[str, Any] | None:
    """Pick highest-scoring plan above threshold."""
    best: tuple[int, dict[str, Any]] | None = None
    for entry in plans:
        score = score_explicit_plan(
            lowered_question,
            entry,
            discovery_celexes,
            legal_issue=legal_issue,
            routing_domain=routing_domain,
        )
        if score < min_score:
            continue
        if best is None or score > best[0]:
            best = (score, entry)
    return best[1] if best else None


def _trigger_matches(text: str, trigger: str) -> bool:
    if len(trigger) <= 5:
        return bool(re.search(rf"\b{re.escape(trigger)}\b", text))
    return trigger in text


def _celex_bonus(question: str, celex: str) -> int:
    if not celex or celex.lower() in question.replace(" ", ""):
        return 40
    return 0


def _directive_number_bonus(question: str, celex: str) -> int:
    """Boost when OJ number in question maps to CELEX (e.g. 2011/83 → 32011L0083)."""
    if not celex or len(celex) < 10:
        return 0
    year = celex[3:7]
    number = celex[8:].lstrip("0") or "0"
    kind = celex[7]
    kind_label = {"L": "richtlijn", "R": "verordening"}.get(kind, "")
    patterns = [
        f"{year}/{number}",
        f"{year}/{number.lstrip('0')}",
        f"{int(year) % 100}/{number}" if year.isdigit() else "",
    ]
    bonus = 0
    for pattern in patterns:
        if pattern and pattern in question:
            bonus = 35
            break
    if kind_label and kind_label in question and bonus:
        bonus += 10
    return bonus
