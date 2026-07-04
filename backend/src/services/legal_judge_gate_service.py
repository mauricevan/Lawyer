"""V7 judge gate — no user-facing answer without adversarial review."""
from typing import Any

from backend.src.services.adversarial_legal_judge_service import AdversarialLegalJudgeService
from backend.src.services.agent_answer_service import AgentAnswerService
from backend.src.services.legal_judge_revision_service import LegalJudgeRevisionService
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.legal_judge import LegalJudgeResult
from shared.schemas.query import QueryRequest


class LegalJudgeGateService:
    """Orchestrate judge → revise/regenerate before final output."""

    def __init__(self) -> None:
        self._judge = AdversarialLegalJudgeService()
        self._reviser = LegalJudgeRevisionService()
        self._answer = AgentAnswerService()

    async def gate(
        self,
        bundle: dict[str, Any],
        request: QueryRequest,
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        evidence: EvidenceValidationResult | None,
        reconciliation: ReconciliationResult | None,
        history: list[dict] | None,
    ) -> tuple[dict[str, Any], LegalJudgeResult | None]:
        """Run V7 adversarial review; revise or block inadequate answers."""
        if not self._should_judge(bundle):
            return bundle, None
        verdict = self._review_bundle(bundle, analysis, plan, fetch)
        if verdict.pass_fail == "pass":
            return bundle, verdict
        if verdict.recommendation == "revise":
            revised_text = self._reviser.revise(
                bundle["answer_text"], verdict.issues_found, analysis,
            )
            re_verdict = self._judge.review(
                revised_text, analysis, plan, fetch.chunks, _celexes(bundle),
            )
            if re_verdict.pass_fail == "pass" or re_verdict.severity != "high":
                return {**bundle, "answer_text": revised_text}, re_verdict
        if verdict.recommendation == "regenerate" and fetch.chunks:
            regenerated = await self._answer.build(
                request, fetch, plan, history, evidence, reconciliation, analysis,
            )
            if self._should_judge(regenerated):
                regen_verdict = self._review_bundle(regenerated, analysis, plan, fetch)
                if regen_verdict.pass_fail == "pass":
                    return regenerated, regen_verdict
                revised = self._reviser.revise(
                    regenerated["answer_text"], regen_verdict.issues_found, analysis,
                )
                return {**regenerated, "answer_text": revised}, regen_verdict
            return regenerated, verdict
        safe = self._reviser.revise(bundle["answer_text"], verdict.issues_found, analysis)
        return {**bundle, "answer_text": safe}, verdict

    def _review_bundle(
        self,
        bundle: dict[str, Any],
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        fetch: AgentFetchResult,
    ) -> LegalJudgeResult:
        return self._judge.review(
            bundle["answer_text"],
            analysis,
            plan,
            fetch.chunks,
            _celexes(bundle),
        )

    def _should_judge(self, bundle: dict[str, Any]) -> bool:
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
