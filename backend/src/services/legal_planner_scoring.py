"""Score explicit legal source plans — best match wins (ADR-0009 maturity)."""
import re
from typing import Any


def score_explicit_plan(
    lowered_question: str,
    entry: dict[str, Any],
    discovery_celexes: frozenset[str] | None = None,
) -> int:
    """Return match score; 0 means no match."""
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
    score += _celex_bonus(lowered_question, str(entry.get("celex", "")))
    score += _directive_number_bonus(lowered_question, str(entry.get("celex", "")))
    if discovery_celexes and str(entry.get("celex", "")) in discovery_celexes:
        score += 45
    return score


def pick_best_explicit_plan(
    lowered_question: str,
    plans: list[dict[str, Any]],
    min_score: int = 10,
    discovery_celexes: frozenset[str] | None = None,
) -> dict[str, Any] | None:
    """Pick highest-scoring plan above threshold."""
    best: tuple[int, dict[str, Any]] | None = None
    for entry in plans:
        score = score_explicit_plan(lowered_question, entry, discovery_celexes)
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
