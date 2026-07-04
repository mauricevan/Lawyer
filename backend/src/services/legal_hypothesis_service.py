"""Form legal hypothesis before retrieval — v3 reasoning step 1."""
import logging
import re

from backend.src.services.legal_question_classifier_service import classify_legal_question
from backend.src.utils.domain_framework_registry import frameworks_for_domain
from backend.src.utils.llm_json_client import call_llm_json
from shared.config.prompt_loader import (
    get_legal_hypothesis_system_prompt,
    get_legal_hypothesis_user_template,
)
from shared.schemas.legal_hypothesis import LegalHypothesis

logger = logging.getLogger(__name__)
_ECOMMERCE_HINTS = ("e-commerce", "webshop", "online winkel", "online verkopen", "vertegenwoordiger")
_EMPLOYMENT_PRE_HIRE = ("sollicitant", "sollicitatie", "medische gegevens", "voor de arbeidsovereenkomst")


class LegalHypothesisService:
    """Analyse question into legal hypothesis without using EUR-Lex sources."""

    async def form(self, question: str, history: list[dict] | None = None) -> LegalHypothesis:
        """Return structured hypothesis; LLM first, rule fallback on failure."""
        try:
            hypothesis = await self._llm_hypothesis(question, history)
            return self._apply_disambiguation(hypothesis, question)
        except Exception as exc:
            logger.warning("LLM legal hypothesis failed: %s", exc)
            return self._rule_hypothesis(question)

    def _apply_disambiguation(self, hypothesis: LegalHypothesis, question: str) -> LegalHypothesis:
        """Correct known cross-domain misroutes after LLM hypothesis."""
        domain = _disambiguate_domain(question, hypothesis.legal_domain_guess)
        actor = _disambiguate_actor(question, hypothesis.legal_actor)
        frameworks = list(hypothesis.likely_eu_frameworks)
        frameworks.extend(_extra_frameworks(question, domain))
        if domain != hypothesis.legal_domain_guess:
            frameworks = _dedupe([*frameworks_for_domain(domain), *frameworks])
        return hypothesis.model_copy(update={
            "legal_actor": actor,
            "legal_domain_guess": domain,
            "likely_eu_frameworks": _dedupe(frameworks)[:8],
        })

    async def _llm_hypothesis(
        self,
        question: str,
        history: list[dict] | None,
    ) -> LegalHypothesis:
        user = get_legal_hypothesis_user_template().format(
            question=question,
            history_block=_format_history(history),
        )
        raw = await call_llm_json(get_legal_hypothesis_system_prompt(), user, max_tokens=500)
        frameworks = raw.get("likely_EU_frameworks") or raw.get("likely_eu_frameworks") or []
        return LegalHypothesis(
            legal_problem=str(raw.get("legal_problem", "")).strip() or _default_problem(question),
            legal_actor=raw.get("legal_actor", "unknown"),
            legal_domain_guess=raw.get("legal_domain_guess", "unknown"),
            likely_eu_frameworks=[str(item).strip() for item in frameworks if str(item).strip()][:8],
            legal_question_type=raw.get("legal_question_type", "unknown"),
            source="llm",
        )

    def _rule_hypothesis(self, question: str) -> LegalHypothesis:
        """Deterministic hypothesis from classifier + domain disambiguation."""
        classification = classify_legal_question(question)
        domain = _disambiguate_domain(question, classification.legal_domain)
        actor = _disambiguate_actor(question, classification.legal_actor)
        frameworks = list(frameworks_for_domain(domain))
        frameworks.extend(_extra_frameworks(question, domain))
        return LegalHypothesis(
            legal_problem=_default_problem(question),
            legal_actor=actor,
            legal_domain_guess=domain,
            likely_eu_frameworks=_dedupe(frameworks)[:8],
            legal_question_type=classification.legal_question_type,
            source="rule",
        )


def _disambiguate_domain(question: str, domain: str) -> str:
    lowered = question.lower()
    if any(h in lowered for h in _EMPLOYMENT_PRE_HIRE):
        return "employment_law"
    return domain


def _disambiguate_actor(question: str, actor: str) -> str:
    lowered = question.lower()
    if any(h in lowered for h in _EMPLOYMENT_PRE_HIRE):
        return "employee"
    if "werkgever" in lowered and actor == "unknown":
        return "employee"
    return actor


def _extra_frameworks(question: str, domain: str) -> list[str]:
    lowered = question.lower()
    extras: list[str] = []
    if domain == "consumer_protection" and any(h in lowered for h in _ECOMMERCE_HINTS):
        extras.append("Directive 2000/31/EC e-commerce country of origin")
    if "vertegenwoordiger" in lowered or "authorized representative" in lowered:
        extras.append("economic operator authorized representative EU")
    return extras


def _default_problem(question: str) -> str:
    trimmed = re.sub(r"\s+", " ", question.strip())
    return trimmed[:400] if trimmed else "EU legal question"


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _format_history(history: list[dict] | None) -> str:
    if not history:
        return ""
    lines = [f"{msg.get('role', 'user')}: {str(msg.get('content', ''))[:200]}" for msg in history[-3:]]
    return "Context:\n" + "\n".join(lines)
