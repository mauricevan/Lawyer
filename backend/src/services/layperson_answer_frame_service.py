"""Layperson answer frame — plan, synoptic lead, and article focus before composition."""
from dataclasses import dataclass
from typing import Literal

from backend.src.services.legal_source_planner_service import LegalSourcePlannerService

AnswerIntent = Literal["permission", "trigger_when", "deadline", "obligation", "general"]


@dataclass(frozen=True)
class LaypersonAnswerFrame:
    """Structured answer goal derived from question + source planner."""

    plan_id: str | None
    celex: str | None
    articles: tuple[str, ...]
    intent: AnswerIntent
    synoptic_lead: str


def resolve_planner_allowed_articles(question: str) -> tuple[str, ...]:
    """Article numbers that may be cited when planner templates ground the answer."""
    frame = resolve_layperson_answer_frame(question)
    if frame is None:
        return ()
    from backend.src.services.legal_planner_template_loader import resolve_obligation_templates

    templates = resolve_obligation_templates(
        frame.plan_id or "",
        frame.celex or "",
        _domain_for_frame(frame.plan_id),
    )
    articles = {str(article) for article in frame.articles if article}
    for template in templates:
        article = str(template.get("article", "")).strip()
        if article and article != "—":
            articles.add(article)
    return tuple(sorted(articles, key=lambda value: int(value) if value.isdigit() else value))


def _domain_for_frame(plan_id: str | None) -> str | None:
    mapping = {
        "gdpr_lawful_basis": "privacy",
        "gdpr_marketing_sharing": "privacy",
        "gpsr_manufacturer_risk": "consumer",
        "consumer_withdrawal": "consumer",
    }
    return mapping.get(plan_id or "")


def resolve_layperson_answer_frame(question: str) -> LaypersonAnswerFrame | None:
    """Return answer frame when a rule-based planner plan matches."""
    plan = LegalSourcePlannerService().plan(question)
    if not plan:
        return None
    intent = _detect_intent(question)
    lead = _synoptic_lead(plan.plan_id, question, intent)
    if not lead:
        return None
    return LaypersonAnswerFrame(
        plan_id=plan.plan_id,
        celex=plan.celex,
        articles=tuple(plan.articles),
        intent=intent,
        synoptic_lead=lead,
    )


def _detect_intent(question: str) -> AnswerIntent:
    lowered = question.lower()
    if any(p in lowered for p in ("wanneer moet", "wanneer mag", "hoe lang", "binnen welke termijn")):
        return "trigger_when" if "terugroep" in lowered or "recall" in lowered else "deadline"
    if any(p in lowered for p in ("mag ik", "mag mijn", "mag een", "mag de", "kan ik")):
        return "permission"
    if any(p in lowered for p in ("moet ik", "moet mijn", "verplicht")):
        return "obligation"
    return "general"


def _synoptic_lead(plan_id: str, question: str, intent: AnswerIntent) -> str | None:
    lowered = question.lower()
    leads = _LEADS_BY_PLAN.get(plan_id, {})
    if intent in leads:
        return leads[intent]
    if "general" in leads:
        return leads["general"]
    if plan_id == "gdpr_lawful_basis" and intent == "permission":
        return _GDPR_MARKETING_PERMISSION
    if plan_id == "gpsr_manufacturer_risk" and intent in {"trigger_when", "obligation"}:
        return _GPSR_RECALL_WHEN
    if plan_id == "consumer_withdrawal" and intent == "deadline":
        return _CONSUMER_WITHDRAWAL_DEADLINE
    if "terugroep" in lowered:
        return _GPSR_RECALL_WHEN
    if "doorgeven" in lowered and any(w in lowered for w in ("reclame", "marketing", "e-mail", "email")):
        return _GDPR_MARKETING_PERMISSION
    if any(w in lowered for w in ("terugsturen", "herroep", "bedenktijd", "koop op afstand")):
        return _CONSUMER_WITHDRAWAL_DEADLINE
    return None


_GDPR_MARKETING_PERMISSION = (
    "**Meestal niet zonder meer.** Een e-mailadres is een persoonsgegeven. Doorgeven aan een "
    "reclamebedrijf is een nieuwe verwerking en mag alleen met een **geldige rechtsgrond** "
    "(bijv. uitdrukkelijke toestemming of — zelden — gerechtvaardigd belang), plus duidelijke "
    "informatie aan u als betrokkene."
)

_GPSR_RECALL_WHEN = (
    "**Zodra u weet of redelijkerwijs moet vermoeden dat het product onveilig is** voor "
    "consumenten. Dan moet u passende maatregelen nemen — dat kan een terugroeping zijn — en "
    "bij ernstige risico's ook de bevoegde autoriteit informeren."
)

_CONSUMER_WITHDRAWAL_DEADLINE = (
    "**In principe 14 dagen** na ontvangst van de goederen bij een **koop op afstand** "
    "(online), zonder dat u een reden hoeft te geven."
)

_LEADS_BY_PLAN: dict[str, dict[AnswerIntent, str]] = {
    "gdpr_lawful_basis": {
        "permission": _GDPR_MARKETING_PERMISSION,
        "general": _GDPR_MARKETING_PERMISSION,
    },
    "gdpr_marketing_sharing": {
        "permission": _GDPR_MARKETING_PERMISSION,
        "general": _GDPR_MARKETING_PERMISSION,
    },
    "gpsr_manufacturer_risk": {
        "trigger_when": _GPSR_RECALL_WHEN,
        "obligation": _GPSR_RECALL_WHEN,
        "general": _GPSR_RECALL_WHEN,
    },
    "consumer_withdrawal": {
        "deadline": _CONSUMER_WITHDRAWAL_DEADLINE,
        "permission": _CONSUMER_WITHDRAWAL_DEADLINE,
        "general": _CONSUMER_WITHDRAWAL_DEADLINE,
    },
}
