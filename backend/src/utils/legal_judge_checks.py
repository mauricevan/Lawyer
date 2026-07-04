"""V7 adversarial judge checks — assume the answer is wrong until proven."""
import re
from dataclasses import dataclass
from typing import Any

from backend.src.utils.layperson_domain_gate import is_weak_kort_antwoord, is_wrong_domain_answer
from backend.src.utils.legal_chunk_text import score_chunk_relevance
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_interpretation import LegalInterpretationPlan
from shared.schemas.legal_judge import JudgeIssueCode, JudgeSeverity

_ABSOLUTE_WORDS = re.compile(
    r"\b(altijd|nooit|zonder uitzondering|absoluut|in alle gevallen|mag niet)\b",
    re.IGNORECASE,
)
_EXCEPTION_WORDS = re.compile(
    r"\b(tenzij|uitzondering|proportional|evenredig|onder voorwaarden|in beginsel|"
    r"mogelijk|kan worden gerechtvaardigd|derogation|mogelijk wel)\b",
    re.IGNORECASE,
)
_UNCONDITIONAL_NO = re.compile(
    r"^\s*\*\*?nee[,.]?\*\*?\s*(lidstaat|de lidstaat|dit|dat)?\s*(mag|kan)\s+niet",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class JudgeFinding:
    """Single adversarial issue."""

    code: JudgeIssueCode
    severity: JudgeSeverity
    detail: str


def run_all_judge_checks(
    answer_text: str,
    analysis: LegalCaseAnalysis,
    plan: LegalInterpretationPlan,
    chunks: list[dict[str, Any]],
    citation_celexes: list[str],
) -> list[JudgeFinding]:
    """Run five mandatory judge checks in adversarial mode."""
    findings: list[JudgeFinding] = []
    findings.extend(_legal_basis_check(answer_text, chunks, citation_celexes))
    findings.extend(_domain_consistency_check(answer_text, plan, citation_celexes))
    findings.extend(_legal_effect_check(answer_text, analysis))
    findings.extend(_exception_check(answer_text, analysis))
    findings.extend(_reasoning_soundness_check(answer_text, analysis, chunks))
    return findings


def _legal_basis_check(
    answer: str,
    chunks: list[dict[str, Any]],
    citation_celexes: list[str],
) -> list[JudgeFinding]:
    findings: list[JudgeFinding] = []
    has_basis_section = "## juridische basis" in answer.lower()
    if not citation_celexes and not has_basis_section and _has_substantive_claim(answer):
        findings.append(JudgeFinding("missing_legal_basis", "high", "Geen juridische basis bij sterke conclusie."))
    if citation_celexes and chunks and not _citations_supported(citation_celexes, chunks, answer):
        findings.append(JudgeFinding("wrong_legal_basis", "high", "Citaten dragen de conclusie niet."))
    return findings


def _domain_consistency_check(
    answer: str,
    plan: LegalInterpretationPlan,
    citation_celexes: list[str],
) -> list[JudgeFinding]:
    if is_wrong_domain_answer(
        answer,
        plan.legal_actor,
        plan.legal_domain,
        citation_celexes,
        plan.legal_question_type,
    ):
        return [JudgeFinding("domain_inconsistency", "high", "Antwoord past niet bij conflict/rechtsgebied.")]
    return []


def _legal_effect_check(answer: str, analysis: LegalCaseAnalysis) -> list[JudgeFinding]:
    if not analysis.legal_effect:
        return []
    findings: list[JudgeFinding] = []
    kort = _kort_section(answer)
    if analysis.legal_effect.effect_conclusion_hint in {"prohibited", "conditional"}:
        if _UNCONDITIONAL_NO.search(kort) and "in beginsel" not in kort.lower():
            findings.append(JudgeFinding("overconfident_conclusion", "high", "Absoluut verbod zonder nuance."))
    if "## juridisch effect" not in answer.lower():
        findings.append(JudgeFinding("missing_effect_section", "medium", "Juridisch effect ontbreekt."))
    if is_weak_kort_antwoord(kort):
        findings.append(JudgeFinding("wrong_legal_effect", "medium", "Kort antwoord mist voorwaardelijke nuance."))
    return findings


def _exception_check(answer: str, analysis: LegalCaseAnalysis) -> list[JudgeFinding]:
    if not analysis.legal_effect:
        return []
    needs_exceptions = analysis.legal_effect.effect_conclusion_hint in {"prohibited", "conditional"}
    if not needs_exceptions:
        return []
    if _EXCEPTION_WORDS.search(answer):
        return []
    return [JudgeFinding("missing_exception_analysis", "medium", "Uitzonderingen/proportionaliteit niet besproken.")]


def _reasoning_soundness_check(
    answer: str,
    analysis: LegalCaseAnalysis,
    chunks: list[dict[str, Any]],
) -> list[JudgeFinding]:
    findings: list[JudgeFinding] = []
    if _ABSOLUTE_WORDS.search(answer) and not _EXCEPTION_WORDS.search(answer):
        findings.append(JudgeFinding("reasoning_jump", "high", "Conclusie te absoluut zonder EU-rechtelijke nuance."))
    if chunks and analysis.legal_effect:
        probe = f"{analysis.legal_effect.legal_effect_type} {analysis.case_summary}"
        if max(score_chunk_relevance(str(c.get("text", "")), probe) for c in chunks) < 2:
            findings.append(JudgeFinding("reasoning_jump", "medium", "Conclusie springt voorbij broninhoud."))
    return findings


def _kort_section(answer: str) -> str:
    match = re.search(r"## Kort antwoord\n(.*?)(?:\n\n## |\Z)", answer, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else answer[:400]


def _has_substantive_claim(answer: str) -> bool:
    kort = _kort_section(answer).lower()
    return any(word in kort for word in ("mag", "moet", "verboden", "toegestaan", "nee", "ja"))


def _citations_supported(celexes: list[str], chunks: list[dict], answer: str) -> bool:
    chunk_celexes = {str(c.get("celex", "")) for c in chunks}
    if not any(celex in chunk_celexes for celex in celexes if celex):
        return False
    probe = _kort_section(answer)
    return any(score_chunk_relevance(str(c.get("text", "")), probe) >= 2 for c in chunks)
