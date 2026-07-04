"""Domain-agnostic layperson prose helpers (kort antwoord, voorbeeld, let op)."""
import re

from backend.src.utils.legal_question_interpretation import LegalActor, infer_legal_actor
from shared.schemas.layperson_clear_answer import ObligationRow

_SUBJECT_BY_ACTOR: dict[LegalActor, str] = {
    "employee": "een werknemer",
    "manufacturer": "een fabrikant",
    "consumer": "een consument",
    "operator": "een exploitant",
    "authority": "een toezichthouder",
    "unknown": "iemand in een vergelijkbare situatie",
}
_PROHIBITION_HINTS = (
    "discriminatie", "ongelijk", "verboden", "mag niet", "ontslagen", "weigeren", "zonder ",
)
_RIGHTS_HINTS = ("welke rechten", "welke verplichtingen", "wat mag ik", "kan ik")
_DEFAULT_LET_OP = (
    "EU-regels worden vaak nationaal ingevuld. Dit is geen persoonlijk juridisch advies."
)


def build_kort_antwoord(
    question: str,
    reg_label: str,
    obligations: list[ObligationRow],
) -> str:
    """Build answer-first opening from question shape and obligation labels."""
    summary = _obligation_summary(obligations)
    polarity = _answer_polarity(question)
    if polarity == "prohibition":
        return (
            f"**Nee, meestal niet.** {reg_label} biedt bescherming tegen ongerechtvaardigde "
            f"behandeling. In het kort: {summary}."
        )
    if polarity == "rights":
        return (
            f"**In principe wel, met voorwaarden.** Op basis van {reg_label} geldt onder meer: "
            f"{summary}."
        )
    if polarity == "conditional":
        return (
            f"**Dat hangt af van de voorwaarden.** {reg_label} stelt onder meer: {summary}. "
            "Zie de uitleg hieronder voor wanneer dit wel of niet mag."
        )
    if obligations:
        return (
            f"Op basis van {reg_label} gelden onder meer: {summary}. "
            "De details staan in de uitleg hieronder."
        )
    return f"Op basis van {reg_label} gelden onder meer regels over uw situatie."


def build_voorbeeld(question: str, obligations: list[ObligationRow]) -> str:
    """Build a short scenario example from actor + obligation themes."""
    actor = infer_legal_actor(question)
    subject = _SUBJECT_BY_ACTOR.get(actor, _SUBJECT_BY_ACTOR["unknown"])
    themes = ", ".join(row.label.lower() for row in obligations[:2]) or "de genoemde regels"
    hook = _scenario_hook(question)
    return (
        f"{hook}{subject.capitalize()} krijgt te maken met een situatie waarin "
        f"{themes} relevant zijn. Noteer feiten, vraag schriftelijk om uitleg en "
        "bewaar correspondentie voor eventuele stappen."
    )


def build_let_op() -> str:
    """Standard limitation disclaimer for template-based answers."""
    return _DEFAULT_LET_OP


def _obligation_summary(obligations: list[ObligationRow]) -> str:
    if not obligations:
        return "de in de wet genoemde rechten en plichten"
    parts = [f"**{row.label.lower()}**" for row in obligations[:3]]
    return ", ".join(parts)


def _answer_polarity(question: str) -> str:
    lowered = question.lower()
    if any(hint in lowered for hint in _PROHIBITION_HINTS):
        return "prohibition"
    if any(hint in lowered for hint in _RIGHTS_HINTS):
        return "rights"
    if re.search(r"\b(mag|kan) (ik|een|mijn)\b", lowered):
        return "conditional"
    return "informative"


def _scenario_hook(question: str) -> str:
    lowered = question.lower()
    if "ontslag" in lowered or "ontslagen" in lowered:
        return "Stel: "
    if "mag" in lowered or "kan ik" in lowered:
        return "Voorbeeld: "
    return ""
