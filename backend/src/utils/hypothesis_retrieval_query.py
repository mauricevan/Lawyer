"""Build EUR-Lex retrieval queries from domain + conflict — never raw question text."""
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_hypothesis import LegalHypothesis


def build_hypothesis_retrieval_query(hypothesis: LegalHypothesis) -> str:
    """V4: retrieval only on legal_domain + primary_legal_conflict."""
    if hypothesis.primary_legal_conflict and hypothesis.legal_domain_guess != "unknown":
        return build_conflict_retrieval_query(
            hypothesis.primary_legal_conflict,
            hypothesis.legal_domain_guess,
        )
    return hypothesis.legal_domain_guess.replace("_", " ")


def build_conflict_retrieval_query(
    conflict: str,
    domain: str,
) -> str:
    """Deterministic retrieval probe from conflict + mapped domain."""
    return f"{conflict.replace('_', ' ')} {domain.replace('_', ' ')}"


def build_analysis_retrieval_query(analysis: LegalCaseAnalysis) -> str:
    """Build retrieval query from V4 case analysis."""
    return build_conflict_retrieval_query(
        analysis.primary_legal_conflict,
        analysis.legal_domain,
    )
