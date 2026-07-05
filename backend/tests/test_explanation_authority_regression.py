"""Regression: published answers must never contain pseudo-judicial headings."""
from backend.src.utils.explanation_authority_guard import has_authority_leak

_FORBIDDEN_SNIPPETS = (
    "## Hof-simulatie",
    "## EU Besluitvorming",
    "Majority Opinion",
    "Score: 87/100",
    "Final judgment",
    "Doctrine-evolutie",
)


def test_golden_samples_have_no_authority_leak() -> None:
    clean = (
        "## Kort antwoord\nHet hangt af van uw situatie.\n\n"
        "## Wat de EU-regels zeggen\nArtikel 5 DSA regelt transparantie.\n\n"
        "## Disclaimer\nGeen advies."
    )
    assert has_authority_leak(clean) is False


def test_golden_leak_detector_catches_known_bad_outputs() -> None:
    for snippet in _FORBIDDEN_SNIPPETS:
        text = f"## Kort antwoord\nOK\n\n{snippet}\nBody"
        assert has_authority_leak(text) is True, snippet
