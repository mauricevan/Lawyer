"""Build EUR-Lex retrieval queries from conflict + legal effect — never raw question."""
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_hypothesis import LegalHypothesis


def build_hypothesis_retrieval_query(hypothesis: LegalHypothesis) -> str:
    """V6: retrieval on conflict + effect type when available."""
    if hypothesis.primary_legal_conflict and hypothesis.legal_domain_guess != "unknown":
        return build_effect_retrieval_query(
            hypothesis.primary_legal_conflict,
            hypothesis.legal_domain_guess,
            hypothesis.legal_effect_type,
        )
    return hypothesis.legal_domain_guess.replace("_", " ")


def build_effect_retrieval_query(
    conflict: str,
    domain: str,
    effect_type: str | None = None,
) -> str:
    """V6 retrieval probe: conflict + effect (+ domain context)."""
    parts = [conflict.replace("_", " ")]
    if effect_type:
        parts.append(effect_type.replace("_", " "))
    parts.append(domain.replace("_", " "))
    return " ".join(parts)


def build_conflict_retrieval_query(conflict: str, domain: str) -> str:
    """Legacy V4 retrieval probe."""
    return build_effect_retrieval_query(conflict, domain, None)


def build_analysis_retrieval_query(analysis: LegalCaseAnalysis) -> str:
    """Build retrieval query from V6 case analysis."""
    effect_type = analysis.legal_effect.legal_effect_type if analysis.legal_effect else None
    return build_effect_retrieval_query(
        analysis.primary_legal_conflict,
        analysis.legal_domain,
        effect_type,
    )
