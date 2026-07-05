"""Apply fail-fast authority guard to answer bundles before user response."""
from typing import Any

from backend.src.utils.explanation_authority_guard import gap_answer_for_authority_leak, has_authority_leak
from shared.schemas.coverage_guidance import AdequacyResult


def guard_bundle_answer(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return gap bundle when authority language is detected; never strip in place."""
    answer = str(bundle.get("answer_text", ""))
    if not answer or not has_authority_leak(answer):
        return bundle
    adequacy = AdequacyResult(
        is_adequate=False,
        reason="insufficient_evidence",
        coverage_status="insufficient",
    )
    return {
        **bundle,
        "answer_text": gap_answer_for_authority_leak(),
        "coverage_status": "insufficient",
        "adequacy": adequacy,
        "citations": [],
    }
