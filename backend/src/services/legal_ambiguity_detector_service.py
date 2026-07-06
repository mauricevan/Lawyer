"""V10.3 detect clear, ambiguous, or unanswerable legal questions."""
import re

from backend.src.utils.defined_term_extractor import extract_defined_term, is_definition_style_question
from backend.src.utils.clarification_patterns import (
    ACTIVITY_HINTS,
    ACTOR_HINTS,
    COMMERCE_HINTS,
    CUSTOMS_HINTS,
    DATA_STORAGE_HINTS,
    EMPLOYMENT_HINTS,
    EU_FACTUAL_ASKS,
    IDENTIFICATION_HINTS,
    LEGAL_INFO_ASKS,
    NON_EU_HINTS,
    PLATFORM_START_HINTS,
    PLATFORM_VAGUE_PATTERN,
    PRIVACY_HINTS,
    SCOPE_HINTS,
)
from shared.schemas.legal_clarification import ClarificationState


class LegalAmbiguityDetectorService:
    """Score ambiguity before EUR-Lex retrieval."""

    def detect(self, question: str) -> tuple[ClarificationState, float, list[str]]:
        """Return state, score 0–1, and human-readable reasons."""
        lowered = question.lower().strip()
        if self._is_non_eu(lowered):
            return "unanswerable", 1.0, ["buiten EU-rechtsgebied"]
        if self._is_definition_lookup(question, lowered):
            return "clear", 0.0, []
        if self._is_decidable_case(lowered):
            return "clear", 0.0, []
        reasons = self._collect_reasons(lowered)
        score = min(1.0, sum(_REASON_WEIGHTS.get(r, 0.1) for r in reasons))
        if score < 0.35 and not reasons:
            return "clear", score, []
        if score < 0.35:
            return "clear", score, reasons
        return "ambiguous", score, reasons

    def has_activity_detail(self, question: str) -> bool:
        lowered = question.lower()
        hits = sum(1 for hint in ACTIVITY_HINTS if hint in lowered)
        return hits >= 2 or len(lowered.split()) >= 18

    def _is_definition_lookup(self, question: str, lowered: str) -> bool:
        """Definition lookups are decidable without ILCL chips when the term is explicit."""
        if not is_definition_style_question(question):
            return False
        return bool(extract_defined_term(question).term)

    def _is_decidable_case(self, lowered: str) -> bool:
        if self._is_clear_operational_question(lowered):
            return True
        if self._is_clear_eu_factual_question(lowered):
            return True
        words = lowered.split()
        if len(words) < 8:
            return False
        if self._is_substantive_legal_info_question(lowered):
            return True
        if len(words) < 10:
            return False
        has_activity = any(h in lowered for h in ACTIVITY_HINTS)
        has_legal_hook = any(
            h in lowered for h in ("platform", "marktplaats", "webshop", "avg", "dsa", "consument", "eu")
        )
        has_question = "?" in lowered or any(p in lowered for p in ("moet ik", "mag ik", "welke"))
        return has_activity and has_legal_hook and has_question

    def _is_substantive_legal_info_question(self, lowered: str) -> bool:
        """Clear enough when EU scope, legal ask, and a recognizable topic are present."""
        has_eu_scope = any(h in lowered for h in SCOPE_HINTS)
        has_legal_ask = any(p in lowered for p in LEGAL_INFO_ASKS) or "?" in lowered
        has_topic = any(
            h in lowered
            for hints in (
                PRIVACY_HINTS, DATA_STORAGE_HINTS, IDENTIFICATION_HINTS,
                COMMERCE_HINTS, EMPLOYMENT_HINTS, PLATFORM_START_HINTS,
                CUSTOMS_HINTS,
            )
            for h in hints
        ) or "platform" in lowered
        return len(lowered.split()) >= 8 and has_eu_scope and has_legal_ask and has_topic

    def _is_clear_eu_factual_question(self, lowered: str) -> bool:
        """Factual EU lookups (scope, member lists, article location) — proceed to research."""
        has_eu_scope = any(h in lowered for h in SCOPE_HINTS) or re.search(r"\beu\b", lowered)
        if any(h in lowered for h in CUSTOMS_HINTS) and "lidstaten" in lowered:
            has_eu_scope = True
        has_factual_ask = self._has_factual_legal_ask(lowered)
        has_topic = any(
            h in lowered
            for hints in (
                CUSTOMS_HINTS, PRIVACY_HINTS, DATA_STORAGE_HINTS, IDENTIFICATION_HINTS,
                COMMERCE_HINTS, EMPLOYMENT_HINTS, PLATFORM_START_HINTS,
            )
            for h in hints
        )
        return has_eu_scope and has_factual_ask and has_topic

    def _has_factual_legal_ask(self, lowered: str) -> bool:
        if "?" in lowered:
            return True
        if any(p in lowered for p in EU_FACTUAL_ASKS):
            return True
        if "welke" in lowered and any(w in lowered for w in ("lidstaten", "landen", "lidstaat")):
            return True
        if any(p in lowered for p in ("waar staat", "in welk artikel", "in welke verordening")):
            return True
        return False

    def _is_non_eu(self, lowered: str) -> bool:
        return any(h in lowered for h in NON_EU_HINTS)

    def _collect_reasons(self, lowered: str) -> list[str]:
        reasons: list[str] = []
        if not any(h in lowered for h in ACTOR_HINTS) and re.search(r"\bik\b", lowered):
            reasons.append("geen actor")
        if not any(h in lowered for h in ACTIVITY_HINTS):
            reasons.append("geen activiteit")
        if any(h in lowered for h in PLATFORM_START_HINTS) or PLATFORM_VAGUE_PATTERN.search(lowered):
            reasons.append("platform-start zonder detail")
        if not any(h in lowered for h in SCOPE_HINTS):
            reasons.append("geen geografische context")
        if self._multi_domain(lowered):
            reasons.append("meerdere EU-domeinen mogelijk")
        if len(lowered) < 20:
            reasons.append("te korte vraag")
        return reasons

    def _multi_domain(self, lowered: str) -> bool:
        domains = 0
        groups = (
            ("platform", "dsa", "marktplaats", "advertent"),
            ("consument", "webshop", "koop", "retour"),
            ("privacy", "avg", "gdpr", "persoonsgegeven"),
            ("arbeid", "werkgever", "werknemer"),
        )
        for hints in groups:
            if any(h in lowered for h in hints):
                domains += 1
        return domains >= 2

    def _is_clear_operational_question(self, lowered: str) -> bool:
        """Short but concrete EU questions that should retrieve without a chip round."""
        permission = (
            "mag ik", "moet ik", "kan ik", "heb ik", "mag mijn", "mag een",
            "moet mijn", "wanneer moet",
        )
        if not any(p in lowered for p in permission):
            return False
        if any(h in lowered for h in DATA_STORAGE_HINTS + PRIVACY_HINTS):
            return True
        if any(h in lowered for h in ("e-mail", "email", "telefoonnummer")):
            return True
        if any(h in lowered for h in ("douane", "invoer", "import", "aangifte", "customs", "etsy")):
            has_trade_context = any(
                h in lowered
                for h in (
                    "china", "pakket", "webshop", "verkopen", "vanuit", "150",
                    "euro", "eur", "derde land", "importeer", "verzenden", "etsy",
                )
            )
            return len(lowered.split()) >= 10 or has_trade_context
        if any(h in lowered for h in ("terugroep", "onveilig", "veiligheidsrisico", "speelgoed")):
            return True
        if any(h in lowered for h in ("terugsturen", "herroep", "bedenktijd", "passen niet", "koop op afstand")):
            return True
        if "gpsr" in lowered or "productveiligheid" in lowered:
            return True
        if any(h in lowered for h in IDENTIFICATION_HINTS):
            return True
        return False


_REASON_WEIGHTS = {
    "geen actor": 0.25,
    "geen activiteit": 0.35,
    "platform-start zonder detail": 0.3,
    "geen geografische context": 0.2,
    "meerdere EU-domeinen mogelijk": 0.2,
    "te korte vraag": 0.35,
}
