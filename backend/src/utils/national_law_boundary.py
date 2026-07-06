"""EU vs national law boundary copy for layperson identity answers."""
from shared.schemas.legal_conflict import LegalCaseAnalysis, PrimaryLegalConflict

_NATIONAL_BOUNDARY = (
    "## EU-recht en nationaal recht\n\n"
    "De EU stelt **niet** in één algemene wet dat iedereen in Europa altijd legitimatie "
    "bij zich moet dragen. EU-recht regelt vooral **welk document** u nodig heeft voor "
    "**vrij verkeer** (paspoort of identiteitskaart) en **elektronische identificatie** "
    "bij (overheids)diensten (eIDAS).\n\n"
    "De algemene plicht om u op verzoek te kunnen identificeren — en soms een document "
    "bij u te dragen — volgt uit **nationaal recht** van de lidstaat. In Nederland o.a. "
    "de Wet op de identificatieplicht. Raadpleeg een jurist of het Juridisch Loket "
    "voor uw concrete situatie."
)


def should_append_national_boundary(analysis: LegalCaseAnalysis | None) -> bool:
    """True when answer should explain EU/national split for identity questions."""
    if not analysis:
        return False
    return analysis.primary_legal_conflict == "identity_verification_issue"


def render_national_law_boundary(analysis: LegalCaseAnalysis | None) -> str:
    """Return markdown block for EU vs national split, or empty string."""
    if not should_append_national_boundary(analysis):
        return ""
    return _NATIONAL_BOUNDARY
