"""Load query intent patterns from shared config."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_PATH = _REPO_ROOT / "shared/config/query_intent_library.yaml"


@dataclass(frozen=True)
class QueryIntent:
    intent_id: str
    patterns: tuple[str, ...]
    domain: str | None
    doc_type: str | None
    celex_hint: str | None
    time_context: str | None
    confidence: float


@lru_cache(maxsize=1)
def load_intent_library() -> tuple[list[QueryIntent], float]:
    with open(_CONFIG_PATH, encoding="utf-8") as handle:
        data: dict[str, Any] = yaml.safe_load(handle)
    threshold = float(data.get("low_confidence_threshold", 0.55))
    intents: list[QueryIntent] = []
    for row in data.get("intents", []):
        intents.append(QueryIntent(
            intent_id=str(row["id"]),
            patterns=tuple(str(p).lower() for p in row.get("patterns", [])),
            domain=row.get("domain"),
            doc_type=row.get("doc_type"),
            celex_hint=row.get("celex_hint"),
            time_context=row.get("time_context"),
            confidence=float(row.get("confidence", 0.8)),
        ))
    intents.sort(key=lambda item: max((len(p) for p in item.patterns), default=0), reverse=True)
    return intents, threshold


def match_intent(question: str) -> QueryIntent | None:
    query_lower = question.lower()
    intents, _ = load_intent_library()
    best: QueryIntent | None = None
    best_len = 0
    for intent in intents:
        for pattern in intent.patterns:
            if pattern in query_lower and len(pattern) > best_len:
                best = intent
                best_len = len(pattern)
    return best
