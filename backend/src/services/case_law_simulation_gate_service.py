"""V8.1 case law simulation gate — structured judgment enforcement."""
from typing import Any

from backend.src.services.case_law_revision_service import CaseLawRevisionService
from backend.src.services.court_simulation_service import CourtSimulationService
from shared.schemas.case_law_simulation import CaseLawSimulationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis


class CaseLawSimulationGateService:
    """Run structured CJEU simulation; fail or revise on structure violations."""

    def __init__(self) -> None:
        self._simulator = CourtSimulationService()
        self._reviser = CaseLawRevisionService()

    def gate(
        self,
        bundle: dict[str, Any],
        analysis: LegalCaseAnalysis,
    ) -> tuple[dict[str, Any], CaseLawSimulationResult | None]:
        """Simulate CJEU review with mandatory arrest structure."""
        if not self._should_simulate(bundle):
            return bundle, None
        simulation = self._simulator.simulate(
            analysis,
            bundle["answer_text"],
            _celexes(bundle),
        )
        if simulation.structure_enforcement == "fail":
            return bundle, simulation
        revised_bundle = self._enforce(bundle, simulation, analysis)
        if simulation.structure_enforcement == "regenerate" or not simulation.structure_valid:
            re_sim = self._simulator.simulate(
                analysis,
                revised_bundle["answer_text"],
                _celexes(revised_bundle),
            )
            return self._enforce(revised_bundle, re_sim, analysis), re_sim
        if simulation.alignment_with_answer == "inconsistent":
            re_sim = self._simulator.simulate(
                analysis,
                revised_bundle["answer_text"],
                _celexes(revised_bundle),
            )
            return self._enforce(revised_bundle, re_sim, analysis), re_sim
        return revised_bundle, simulation

    def _enforce(
        self,
        bundle: dict[str, Any],
        simulation: CaseLawSimulationResult,
        analysis: LegalCaseAnalysis,
    ) -> dict[str, Any]:
        revised = self._reviser.revise(bundle["answer_text"], simulation, analysis)
        return {**bundle, "answer_text": revised}

    def _should_simulate(self, bundle: dict[str, Any]) -> bool:
        if bundle.get("coverage_status") == "insufficient":
            return False
        text = str(bundle.get("answer_text", "")).strip()
        return bool(text) and "## kort antwoord" in text.lower()


def _celexes(bundle: dict[str, Any]) -> list[str]:
    citations = bundle.get("citations") or []
    celexes: list[str] = []
    for citation in citations:
        celex = getattr(citation, "celex", None)
        if celex:
            celexes.append(str(celex))
            continue
        if isinstance(citation, dict) and citation.get("celex"):
            celexes.append(str(citation["celex"]))
    return celexes
