"""Tests for explanation authority leak detection."""
from backend.src.utils.explanation_authority_guard import has_authority_leak


def test_detects_hof_simulatie_heading() -> None:
    text = "## Kort antwoord\nTest\n\n## Hof-simulatie\nIssue"
    assert has_authority_leak(text) is True


def test_detects_majority_opinion_phrase() -> None:
    assert has_authority_leak("### 3. Majority Opinion\nText") is True


def test_detects_score_pattern() -> None:
    assert has_authority_leak("**Score: 87/100**") is True


def test_detects_court_simulation_phrase() -> None:
    text = "The measure constitutes a disproportionate restriction incompatible with Article 56 TFEU."
    assert has_authority_leak(text) is True


def test_clean_explanation_passes() -> None:
    text = (
        "## Kort antwoord\nHet hangt af van uw situatie.\n\n"
        "## Wat de EU-regels zeggen\nArtikel 5 DSA regelt …"
    )
    assert has_authority_leak(text) is False
