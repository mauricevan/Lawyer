"""V7 adversarial legal judge — stress-test answers before user output."""
from typing import Any

from backend.src.utils.legal_judge_checks import JudgeFinding, run_all_judge_checks
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_interpretation import LegalInterpretationPlan
from shared.schemas.legal_judge import (
    JudgeIssueCode,
    JudgeRecommendation,
    JudgeSeverity,
    LegalJudgeResult,
)

_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


class AdversarialLegalJudgeService:
    """Critical EU-law expert role: try to break the draft answer."""

    def review(
        self,
        answer_text: str,
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        chunks: list[dict[str, Any]],
        citation_celexes: list[str],
    ) -> LegalJudgeResult:
        """Assume answer is wrong; return pass only if all checks survive."""
        findings = run_all_judge_checks(answer_text, analysis, plan, chunks, citation_celexes)
        if not findings:
            return LegalJudgeResult(pass_fail="pass", recommendation="approve")
        return self._verdict_from_findings(findings)

    def _verdict_from_findings(self, findings: list[JudgeFinding]) -> LegalJudgeResult:
        severity = self._max_severity(findings)
        issues = list(dict.fromkeys(finding.code for finding in findings))[:10]
        recommendation = self._recommend(severity)
        pass_fail = "pass" if recommendation == "approve" else "fail"
        rationale = "; ".join(finding.detail for finding in findings[:3])
        return LegalJudgeResult(
            pass_fail=pass_fail,  # type: ignore[arg-type]
            issues_found=issues,
            severity=severity,
            recommendation=recommendation,
            rationale=rationale,
        )

    def _max_severity(self, findings: list[JudgeFinding]) -> JudgeSeverity:
        return max((finding.severity for finding in findings), key=lambda s: _SEVERITY_RANK[s])

    def _recommend(self, severity: JudgeSeverity) -> JudgeRecommendation:
        if severity == "high":
            return "regenerate"
        if severity in {"medium", "low"}:
            return "revise"
        return "approve"
