"""Template answers for CN/TARIC classification questions."""
from shared.config.cn_classification_loader import get_cn_referrals
from backend.src.services.cn_classification_service import CnPositionMatch

_CLASSIFICATION_DISCLAIMER = (
    "Dit is **geen bindende douane-classificatie**. Alleen de douane of een BTI-beschikking "
    "is definitief. Raadpleeg TARIC of een douane-expediteur voor uw concrete zending."
)


class CnClassificationAnswerService:
    """Builds deterministic markdown for known CN position questions."""

    def build(self, match: CnPositionMatch, audience: str = "layperson") -> str:
        if audience == "professional":
            return self._build_professional(match)
        return self._build_layperson(match)

    def _build_layperson(self, match: CnPositionMatch) -> str:
        sections = [f"## Kort antwoord\n{self._short_answer(match)}"]
        sections.append(f"## Toelichting\n{match.summary_nl}")
        if match.subheading:
            sections.append(self._subheading_section(match))
        else:
            sections.append(self._generic_precision_section(match))
        sections.append(self._referrals_section())
        sections.append(f"## Let op\n{_CLASSIFICATION_DISCLAIMER}")
        return "\n\n".join(sections)

    def _build_professional(self, match: CnPositionMatch) -> str:
        lines = [self._short_answer(match), "", match.summary_nl]
        if match.subheading:
            lines.append(f"- Aanbevolen subheading: **{match.subheading.code}** — {match.subheading.label_nl}")
        lines.append(f"- Kader: {match.regulation_title} (CELEX {match.regulation_celex})")
        for referral in get_cn_referrals():
            lines.append(f"- [{referral['label']}]({referral['url']})")
        lines.append(f"\n**Let op:** {_CLASSIFICATION_DISCLAIMER}")
        return "\n".join(lines)

    def _short_answer(self, match: CnPositionMatch) -> str:
        if match.subheading:
            return (
                f"Positie **{match.position_code}** ({match.title_nl}) is de **juiste hoofdgroep**. "
                f"Voor een paard van zuiver ras als fokdier past doorgaans "
                f"**{match.subheading.code}** — niet alleen de viercijferige code **{match.position_code}**."
            )
        return (
            f"Positie **{match.position_code}** ({match.title_nl}) lijkt passend, "
            f"maar controleer de **8-cijferige CN-code** en TARIC voor uw specifieke zending."
        )

    def _subheading_section(self, match: CnPositionMatch) -> str:
        assert match.subheading is not None
        return (
            "## Meest waarschijnlijke CN-subindeling\n"
            f"- **{match.subheading.code}** — {match.subheading.label_nl}\n"
            "- Declareer niet alleen vier cijfers; de EU-douane gebruikt doorgaans **8 cijfers (CN)** "
            "en soms **10 cijfers (TARIC)** met maatregelen per land van herkomst."
        )

    def _generic_precision_section(self, match: CnPositionMatch) -> str:
        return (
            "## Precisie van de code\n"
            f"- **{match.position_code}** is een positie, geen volledige aangiftecode.\n"
            "- Controleer in TARIC welke subcodes, documenten en rechten gelden."
        )

    def _referrals_section(self) -> str:
        bullets = "\n".join(
            f"- [{item['label']}]({item['url']})" for item in get_cn_referrals()
        )
        return f"## Waar u de code kunt controleren\n{bullets}"
