"""Unit tests for effective question merge (Step 1)."""
from backend.src.utils.clarification_history_merge import merge_clarification_history
from backend.src.utils.effective_question_resolver import resolve_effective_question
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator

CLARIFY_META = {
    "coverage_status": "clarify_only",
    "verification_questions": ["ondernemer", "consument / particulier"],
}


def _history(q1: str, a1_meta: dict | None = None) -> list[dict]:
    return [
        {"role": "user", "content": q1},
        {
            "role": "assistant",
            "content": "clarify",
            "metadata": a1_meta or CLARIFY_META,
        },
    ]


def test_merge_preserves_chatbot_after_role_chip():
    q1 = "Moet ik mijn chatbot registreren?"
    merged = resolve_effective_question("ondernemer", _history(q1))
    assert "chatbot" in merged.lower()
    result = LegalClarificationOrchestrator().clarify("ondernemer", history=_history(q1))
    assert "chatbot" in (result.enriched_question or "").lower()


def test_merge_preserves_data_context_after_consument():
    q1 = "Mag ik data van klanten opslaan?"
    merged = resolve_effective_question("consument", _history(q1))
    assert "data" in merged.lower() or "klant" in merged.lower()


def test_merge_preserves_webshop_or_marktplaats_correction():
    q1 = "Mag ik een webshop beginnen?"
    q2 = "nee ik bedoel eigenlijk een marktplaats voor tweedehands spullen"
    merged = resolve_effective_question(q2, _history(q1))
    assert "webshop" in merged.lower() or "marktplaats" in merged.lower()


def test_merge_preserves_ontslaan_context():
    q1 = "Kan mijn baas me zomoar ontslaan?"
    merged = resolve_effective_question(
        "ik werk al 3 jaar bij hetzelfde bedrijf",
        _history(q1),
    )
    assert "ontslaan" in merged.lower() or "ontslag" in merged.lower()


def test_merge_skips_already_merged_question():
    history = [
        {"role": "user", "content": "mag ik een platform bouwen"},
        {"role": "assistant", "content": "clarify", "metadata": CLARIFY_META},
        {"role": "user", "content": "contentwebsite"},
    ]
    merged = merge_clarification_history(
        "mag ik een platform bouwen — verduidelijking: contentwebsite",
        history,
    )
    assert merged.count("verduidelijking:") == 1


def test_clarify_only_without_chips_still_merges():
    history = [
        {"role": "user", "content": "Kan mijn baas me zomoar ontslaan?"},
        {
            "role": "assistant",
            "content": "clarify",
            "metadata": {"coverage_status": "clarify_only", "verification_questions": []},
        },
    ]
    merged = merge_clarification_history("ontslag", history)
    assert "baas" in merged.lower() or "ontslaan" in merged.lower()
