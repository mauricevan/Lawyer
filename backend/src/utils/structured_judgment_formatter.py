"""V8.1 structured judgment formatter — mandatory arrest output."""
from shared.schemas.case_law_simulation import StructuredJudgment

_REQUIRED_HEADINGS = (
    "### 1. Issue",
    "### 2. Applicable EU Law",
    "### 3. Restriction Analysis",
    "### 4. Legitimate Aim",
    "### 5. Proportionality Test",
    "#### 5.1 Suitability",
    "#### 5.2 Necessity",
    "#### 5.3 Balancing",
    "### 6. Court Conclusion",
    "### 7. Legal Effect Classification",
)


def format_structured_judgment(judgment: StructuredJudgment) -> str:
    """Render the fixed seven-section CJEU arrest format."""
    laws = "\n".join(judgment.applicable_eu_law)
    return (
        "## Hof-simulatie\n\n"
        f"### 1. Issue\n\n{judgment.issue}\n\n"
        f"### 2. Applicable EU Law\n\n{laws}\n\n"
        f"### 3. Restriction Analysis\n\n{judgment.restriction_analysis}\n\n"
        f"### 4. Legitimate Aim\n\n{judgment.legitimate_aim}\n\n"
        f"### 5. Proportionality Test\n\n"
        f"#### 5.1 Suitability\n\n{judgment.proportionality.suitability}\n\n"
        f"#### 5.2 Necessity\n\n{judgment.proportionality.necessity}\n\n"
        f"#### 5.3 Balancing\n\n{judgment.proportionality.balancing}\n\n"
        f"### 6. Court Conclusion\n\n{judgment.court_conclusion}\n\n"
        f"### 7. Legal Effect Classification\n\n{judgment.legal_effect_classification}"
    )


def validate_structured_judgment_text(text: str, judgment: StructuredJudgment | None = None) -> bool:
    """Return True only when all mandatory headings and proportionality steps exist."""
    if not text.strip():
        return False
    for heading in _REQUIRED_HEADINGS:
        if heading not in text:
            return False
    if _has_free_text_intro(text):
        return False
    if judgment and not judgment.proportionality.is_complete:
        return False
    if judgment and not judgment.legal_effect_classification:
        return False
    return True


def _has_free_text_intro(text: str) -> bool:
    """Reject narrative intros outside section 6."""
    body = text.split("### 6. Court Conclusion")[0]
    banned = (
        "in beginsel niet toegestaan",
        "de eu-rechter zou waarschijnlijk",
        "eindconclusie hof",
        "reasoning summary",
    )
    lower = body.lower()
    return any(phrase in lower for phrase in banned)
