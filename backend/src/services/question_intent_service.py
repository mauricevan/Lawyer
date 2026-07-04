"""Intent analysis for EU regulation Q&A (system instruction v1.0)."""
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_RULES_PATH = _REPO_ROOT / "shared/config/question_intent_rules.yaml"
_ARTICLE_RE = re.compile(r"(?i)(?:artikel|article|art\.)\s*(\d+[a-z]?(?:\(\d+\))?)")


@dataclass(frozen=True)
class QuestionIntentAnalysis:
    question_type: str
    specificity: str
    legal_domain: str | None
    article_refs: tuple[str, ...]
    requires_rag_pipeline: bool
    suggested_celex: str | None
    eurlex_search_terms: tuple[str, ...]


@lru_cache(maxsize=1)
def _load_rules() -> dict[str, Any]:
    with open(_RULES_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class QuestionIntentService:
    """Detects specific vs generic EU legal questions before retrieval."""

    def analyze(self, question: str) -> QuestionIntentAnalysis:
        rules = _load_rules()
        lowered = question.lower()
        article_refs = tuple(dict.fromkeys(_ARTICLE_RE.findall(question)))
        has_specific = self._matches_any(lowered, rules.get("specific_triggers", []))
        has_generic = self._matches_any(lowered, rules.get("generic_triggers", []))
        domain = self._detect_domain(lowered, rules.get("legal_domains", {}))
        question_type = self._detect_question_type(lowered, article_refs)
        requires_rag = bool(article_refs or (has_specific and not has_generic))
        if has_specific and has_generic and article_refs:
            requires_rag = True
        specificity = "specific" if requires_rag else ("generic" if has_generic else "general")
        celex = self._suggested_celex(domain, rules.get("legal_domains", {}))
        terms = self._search_terms(question, domain, article_refs)
        return QuestionIntentAnalysis(
            question_type=question_type,
            specificity=specificity,
            legal_domain=domain,
            article_refs=article_refs,
            requires_rag_pipeline=requires_rag,
            suggested_celex=celex,
            eurlex_search_terms=terms,
        )

    def is_registry_intro_topic(self, topic_id: str) -> bool:
        rules = _load_rules()
        return topic_id in rules.get("registry_intro_topic_ids", [])

    def forbidden_generic_phrases(self) -> tuple[str, ...]:
        return tuple(_load_rules().get("forbidden_generic_phrases", []))

    def _matches_any(self, text: str, triggers: list[str]) -> bool:
        return any(str(trigger).lower() in text for trigger in triggers)

    def _detect_domain(self, text: str, domains: dict[str, Any]) -> str | None:
        for name, cfg in domains.items():
            keywords = [str(k).lower() for k in cfg.get("keywords", [])]
            if any(keyword in text for keyword in keywords):
                return str(name)
        return None

    def _detect_question_type(self, text: str, article_refs: tuple[str, ...]) -> str:
        if article_refs or "welke artikelen" in text or "relevante artikelen" in text:
            return "article_lookup"
        if text.startswith("wat is het verschil") or "verschil tussen" in text:
            return "comparison"
        if text.startswith("wat is ") or "uitleg" in text:
            return "definition"
        if any(token in text for token in ("mag ik", "mag een", "kan ik", "mag de")):
            return "procedural"
        if "termijn" in text or "procedure" in text or "hoe vraag ik" in text:
            return "procedural"
        return "general"

    def _suggested_celex(self, domain: str | None, domains: dict[str, Any]) -> str | None:
        if not domain:
            return None
        cfg = domains.get(domain, {})
        return cfg.get("primary_celex")

    def _search_terms(
        self, question: str, domain: str | None, article_refs: tuple[str, ...],
    ) -> tuple[str, ...]:
        words = re.findall(r"[A-Za-zÀ-ÿ0-9-/]{4,}", question.lower())
        terms = list(words[:6])
        if article_refs:
            terms[:0] = [f"artikel {ref}" for ref in article_refs[:3]]
        if domain == "customs":
            terms.append("UCC 952/2013")
        return tuple(dict.fromkeys(terms))
