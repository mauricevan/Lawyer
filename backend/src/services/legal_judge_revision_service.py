"""V7 answer revision after partial judge failure."""
import re

from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_effect import LegalEffectAnalysis
from shared.schemas.legal_judge import JudgeIssueCode

_EXCEPTION_BLOCK = (
    "EU-recht laat in uitzonderingsgevallen ruimte wanneer een maatregel gerechtvaardigd, "
    "evenredig en noodzakelijk is (bijvoorbeeld op grond van een TFEU-rechtvaardiging of "
    "een specifieke afwijkingsbepaling in een richtlijn). Dat moet per concrete maatregel "
    "worden beoordeeld."
)


class LegalJudgeRevisionService:
    """Auto-refactor draft answers without showing the user the failed version."""

    def revise(
        self,
        answer_text: str,
        issues: list[JudgeIssueCode],
        analysis: LegalCaseAnalysis,
    ) -> str:
        """Apply targeted fixes for low/medium judge issues."""
        revised = answer_text
        if "overconfident_conclusion" in issues or "wrong_legal_effect" in issues:
            revised = self._soften_kort_antwoord(revised, analysis.legal_effect)
        if "missing_exception_analysis" in issues or "reasoning_jump" in issues:
            revised = self._append_exception_section(revised)
        if "missing_effect_section" in issues and analysis.legal_effect:
            from backend.src.services.legal_effect_answer_service import enrich_layperson_answer
            revised = enrich_layperson_answer(revised, analysis.legal_effect)
        return revised

    def _soften_kort_antwoord(self, answer: str, effect: LegalEffectAnalysis | None) -> str:
        kort = _kort_section(answer)
        if "in beginsel" in kort.lower():
            return answer
        softened = "**In beginsel niet toegestaan**, tenzij de maatregel gerechtvaardigd en evenredig is."
        if effect and effect.effect_conclusion_hint == "conditional":
            softened = "**Alleen toegestaan onder strikte voorwaarden**; een absoluut verbod is niet zonder meer juist."
        return re.sub(
            r"(## Kort antwoord\n)(.*?)(\n\n## )",
            rf"\1{softened}\n\n\3",
            answer,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )

    def _append_exception_section(self, answer: str) -> str:
        if _EXCEPTION_BLOCK.lower()[:40] in answer.lower():
            return answer
        marker = "## Juridische basis"
        if marker.lower() in answer.lower():
            return answer.replace(marker, f"## Uitzonderingen en nuance\n{_EXCEPTION_BLOCK}\n\n{marker}", 1)
        return f"{answer.rstrip()}\n\n## Uitzonderingen en nuance\n{_EXCEPTION_BLOCK}"


def _kort_section(answer: str) -> str:
    match = re.search(r"## Kort antwoord\n(.*?)(?:\n\n## |\Z)", answer, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else answer[:400]
