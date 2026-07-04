"""V8.1 answer revision — enforce structured arrest format only."""
import re

from shared.schemas.case_law_simulation import CaseLawSimulationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis


class CaseLawRevisionService:
    """Replace Hof-simulatie with mandatory structured judgment; align kort antwoord."""

    def revise(
        self,
        answer_text: str,
        simulation: CaseLawSimulationResult,
        analysis: LegalCaseAnalysis,
    ) -> str:
        """Inject structured judgment and align kort antwoord from section 6/7."""
        revised = answer_text
        if simulation.alignment_with_answer == "inconsistent":
            revised = self._align_kort_antwoord(revised, simulation)
        return self._replace_court_section(revised, simulation)

    def _align_kort_antwoord(self, answer: str, simulation: CaseLawSimulationResult) -> str:
        if not simulation.structured_judgment:
            return answer
        conclusion = simulation.structured_judgment.court_conclusion
        effect = simulation.structured_judgment.legal_effect_classification
        replacement = f"**{conclusion}** ({effect})."
        return re.sub(
            r"(## Kort antwoord\n)(.*?)(\n\n## )",
            rf"\1{replacement}\n\n\3",
            answer,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )

    def _replace_court_section(self, answer: str, simulation: CaseLawSimulationResult) -> str:
        formatted = simulation.formatted_judgment
        if not formatted:
            return answer
        if "## Hof-simulatie" in answer:
            return re.sub(
                r"## Hof-simulatie.*?(?=\n## |\Z)",
                formatted.rstrip(),
                answer,
                count=1,
                flags=re.DOTALL,
            )
        marker = "## Juridische basis"
        if marker.lower() in answer.lower():
            return answer.replace(marker, f"{formatted}\n\n{marker}", 1)
        return f"{answer.rstrip()}\n\n{formatted}"
