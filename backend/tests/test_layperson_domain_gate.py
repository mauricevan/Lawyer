"""Tests for layperson domain gate."""
from backend.src.utils.layperson_domain_gate import is_weak_kort_antwoord, is_wrong_domain_answer


def test_weak_unconditional_ja():
    assert is_weak_kort_antwoord("**Ja.** de GPSR regelt onder meer veilig product.")


def test_ja_with_conditions_ok():
    assert not is_weak_kort_antwoord("Nee, in principe niet zonder CE-markering waar verplicht.")


def test_rejects_enforcement_douane_noise():
    answer = "## Kort antwoord\n**Ja.** Douaneautoriteit en douaneregeling.\n## Uitleg\nICS."
    assert is_wrong_domain_answer(
        answer, "authority", "administrative_law", ["32019R1020"], "enforcement",
    )


def test_rejects_mar_citation_for_administrative_law():
    answer = "## Kort antwoord\nEen toezichthouder mag ingrijpen.\n## Uitleg\nMarktmisbruik."
    assert is_wrong_domain_answer(
        answer, "authority", "administrative_law", ["32014R0596"],
    )
