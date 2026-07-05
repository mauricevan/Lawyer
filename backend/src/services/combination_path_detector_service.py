"""Detect explicit multi-part legal questions that require combination-path routing."""
from __future__ import annotations

import re
from dataclasses import dataclass

from backend.src.services.layperson_clarification_guide_service import (
    LaypersonClarificationGuideService,
)
from backend.src.utils.question_typo_normalizer import normalize_question_typos

_GUIDE = LaypersonClarificationGuideService()

_RELATIVE_DATA_CLAUSE = re.compile(
    r"\s+en\s+(data|gegeven|gegevens|klant|klanten|email|e-mail|cookie|privacy)\s+"
    r"(verzam|opsla|bewaar|gebruik|doorgeef)",
    re.I,
)
_SPLIT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\s+en\s+(hoe|wat|moet|mag|is)\s+", re.I), "en"),
    (re.compile(r"\s+of\s+(moet|mag)\s+(ik\s+)?", re.I), "of"),
    (re.compile(r"\?\s*(en|of)\s+(hoe|wat|moet|mag)\s+", re.I), "punct"),
)

_PRIVACY_KEYWORDS = (
    "avg",
    "gegeven",
    "gegevens",
    "persoonsgegeven",
    "data",
    "toestemming",
    "privacy",
    "cookie",
)
_REGISTRATION_KEYWORDS = ("registr", "aanmel", "melden", "aanmelden")
_PLATFORM_KEYWORDS = ("marktplaats", "platform", "app ", "saas", "webshop", "marktplaats-app")


@dataclass(frozen=True)
class CombinationPart:
    """Single sub-question within a combination path."""

    text: str
    branch: str
    branch_label: str


@dataclass(frozen=True)
class CombinationPlan:
    """Split question with distinct G3 branches per part."""

    original_question: str
    parts: tuple[CombinationPart, ...]
    split_marker: str


_BRANCH_LABELS = {
    "§4": "Gegevens / privacy (AVG)",
    "§5": "Registratie / aanmelding (AI-tool)",
    "§6": "Platform / marktplaats",
}


def detect_combination_plan(question: str) -> CombinationPlan | None:
    """Return a combination plan when two distinct G3 branches are explicitly asked."""
    normalized = normalize_question_typos(question.strip())
    if not normalized or _is_relative_data_clause(normalized):
        return None
    split = _find_split(normalized)
    if split is None:
        return None
    part_a, part_b, marker = split
    branch_a = map_g3_branch(part_a)
    branch_b = map_g3_branch(part_b)
    if branch_a == branch_b:
        return None
    return CombinationPlan(
        original_question=normalized,
        split_marker=marker,
        parts=(
            _part(part_a, branch_a),
            _part(part_b, branch_b),
        ),
    )


def map_g3_branch(question: str) -> str:
    """Map a sub-question to G3 branch label (§4 / §5 / §6)."""
    lowered = question.lower()
    has_privacy = any(k in lowered for k in _PRIVACY_KEYWORDS)
    has_reg = any(k in lowered for k in _REGISTRATION_KEYWORDS)
    has_platform = any(k in lowered for k in _PLATFORM_KEYWORDS)
    if has_privacy and not has_reg:
        return "§4"
    if has_reg and has_platform:
        return "§6"
    if has_reg:
        return "§5"
    if has_platform:
        return "§6"
    topic = _GUIDE._detect_topic(normalize_question_typos(question))  # noqa: SLF001
    return {"privacy": "§4", "data_storage": "§4", "platform": "§6"}.get(topic, "§5")


def branch_display_label(branch: str) -> str:
    """Human-readable section title for a G3 branch."""
    return _BRANCH_LABELS.get(branch, branch)


def _part(text: str, branch: str) -> CombinationPart:
    return CombinationPart(text=text, branch=branch, branch_label=branch_display_label(branch))


def _is_relative_data_clause(text: str) -> bool:
    """Exclude implicit overlap like 'chatbot … en data verzamelt'."""
    if not _RELATIVE_DATA_CLAUSE.search(text):
        return False
    return _find_split(text, ignore_relative=False) is None


def _find_split(text: str, *, ignore_relative: bool = True) -> tuple[str, str, str] | None:
    for pattern, marker in _SPLIT_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if ignore_relative and marker == "en" and _RELATIVE_DATA_CLAUSE.search(text):
            continue
        part_a = text[: match.start()].strip()
        part_b = re.sub(r"^(en|of)\s+", "", text[match.start() :].strip(), flags=re.I)
        if not part_a or not part_b:
            continue
        if not part_a.endswith("?"):
            part_a = f"{part_a.rstrip('.')}?"
        return part_a, part_b, marker
    return None
