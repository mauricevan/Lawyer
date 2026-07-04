"""Template-only answers when EUR-Lex context is insufficient."""
from backend.src.services.question_intent_service import QuestionIntentAnalysis
from shared.schemas.coverage_guidance import CoverageGuidance, CoverageReason

LEGAL_NOTICE = (
    "Dit is geen persoonlijk juridisch advies. Raadpleeg een advocaat "
    "of de genoemde instanties voor uw specifieke situatie."
)
SPECIFIC_LEGAL_NOTICE = (
    "Dit is algemene juridische informatie, geen persoonlijk advies. "
    "Raadpleeg een douane-expediteur of uw bevoegde douaneautoriteit voor uw specifieke situatie."
)
IRRELEVANT_SOURCES_NOTICE = (
    "De gevonden bronnen gaan niet over uw vraag; ik licht ze daarom niet toe."
)


class InsufficientCoverageAnswerService:
    """Builds deterministic markdown for inadequate retrieval."""

    def build(
        self,
        guidance: CoverageGuidance,
        reason: CoverageReason,
        audience: str = "layperson",
        question: str = "",
        intent: QuestionIntentAnalysis | None = None,
    ) -> str:
        if intent and self._uses_specific_gap(intent, audience):
            return self._build_specific_gap(guidance, reason, question, intent, audience)
        if audience == "professional":
            return self._build_professional(guidance, reason)
        return self._build_layperson(guidance, reason, question)

    @staticmethod
    def _uses_specific_gap(intent: QuestionIntentAnalysis, audience: str) -> bool:
        if not intent.requires_rag_pipeline:
            return False
        return audience == "professional" or intent.question_type == "article_lookup"

    def _build_layperson(
        self, guidance: CoverageGuidance, reason: CoverageReason, question: str = "",
    ) -> str:
        opener = guidance.empathy_opener.strip()
        ack = self._question_acknowledgment(question)
        base = (
            f"{opener} Ik kan hier geen betrouwbaar antwoord op geven op basis van "
            "de EU-bronnen die ik heb."
        ).strip() if opener else (
            "Ik kan hier geen betrouwbaar antwoord op geven op basis van "
            "de EU-bronnen die ik heb."
        )
        short = f"{ack}{base}" if ack else base
        sections = [f"## Kort antwoord\n{short}"]
        if reason == "irrelevant_retrieval":
            sections.append(f"\n{IRRELEVANT_SOURCES_NOTICE}")
        if reason == "fetch_attempted":
            sections.append(
                "\nDe gevraagde artikeltekst kon niet volledig worden opgehaald van EUR-Lex."
            )
        sections.append(self._next_steps_section(guidance))
        sections.append(f"## Let op\n{LEGAL_NOTICE}")
        return "\n".join(sections)

    def _build_specific_gap(
        self,
        guidance: CoverageGuidance,
        reason: CoverageReason,
        question: str,
        intent: QuestionIntentAnalysis,
        audience: str,
    ) -> str:
        subject = self._subject_snippet(question)
        terms = ", ".join(intent.eurlex_search_terms[:5]) or subject
        opener = (
            f"Op basis van de beschikbare bronnen kon geen specifieke wettekst worden gevonden "
            f"die uw vraag over {subject} direct beantwoordt."
        )
        sections = [f"## Kort antwoord\n{opener}"]
        if reason == "irrelevant_retrieval":
            sections.append(f"\n{IRRELEVANT_SOURCES_NOTICE}")
        sections.append(
            "## Wat u concreet kunt doen\n"
            f"1. Zoek via [EUR-Lex](https://eur-lex.europa.eu/) met: {terms}.\n"
            f"2. {self._referral_line(guidance)}"
        )
        notice = SPECIFIC_LEGAL_NOTICE if intent.legal_domain == "customs" else LEGAL_NOTICE
        sections.append(f"## Let op\n{notice}")
        return "\n".join(sections)

    def _subject_snippet(self, question: str) -> str:
        cleaned = " ".join(question.split()).strip()
        if len(cleaned) <= 60:
            return cleaned.lower()
        return f"{cleaned[:57].lower()}…"

    def _referral_line(self, guidance: CoverageGuidance) -> str:
        if guidance.referrals:
            item = guidance.referrals[0]
            return f"Voor zekerheid: raadpleeg [{item.label}]({item.url})."
        if guidance.frameworks:
            return f"Voor zekerheid: raadpleeg {guidance.frameworks[0].name}."
        return "Voor zekerheid: raadpleeg een bevoegde autoriteit."

    def _question_acknowledgment(self, question: str) -> str:
        cleaned = " ".join(question.split()).strip()
        if len(cleaned) < 12:
            return ""
        snippet = cleaned if len(cleaned) <= 80 else f"{cleaned[:77]}…"
        return f"U vraagt naar: {snippet} "

    def _build_professional(self, guidance: CoverageGuidance, reason: CoverageReason) -> str:
        lines = [
            "Onvoldoende EUR-Lex-context voor een betrouwbaar antwoord.",
        ]
        if reason == "irrelevant_retrieval":
            lines.append(IRRELEVANT_SOURCES_NOTICE)
        for framework in guidance.frameworks[:2]:
            lines.append(f"- **{framework.name}:** {framework.summary}")
        lines.append(f"\n**Let op:** {LEGAL_NOTICE}")
        return "\n".join(lines)

    def _next_steps_section(self, guidance: CoverageGuidance) -> str:
        frameworks = guidance.frameworks[:2]
        referrals = guidance.referrals[:3]
        bullets = "\n".join(
            f"- **{item.name}:** {item.summary}" for item in frameworks
        )
        links = "\n".join(
            f"- [{item.label}]({item.url})" for item in referrals
        )
        return f"## Wat u wél kunt doen\n{bullets}\n{links}"
