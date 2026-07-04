"""Tests for layperson answer formatting."""
from backend.src.utils.layperson_answer_formatter import (
    ensure_layperson_sections,
    has_required_sections,
    is_weak_layperson_answer,
    replace_fallback_boilerplate,
    strip_technical_noise,
)

FALLBACK_INPUT = (
    "## Kort antwoord\n"
    "Op basis of CELEX:32016R0679 lijkt artikel 6 relevant voor uw vraag.\n\n"
    "## Uitleg\nSkip to main content http://publications.europa.eu\n"
)

BOILERPLATE = (
    "## Kort antwoord\nDe regels over - NL zijn relevant voor uw vraag.\n\n"
    "## Uitleg\nGezien het voorstel van de Commissie..."
)


def test_strip_technical_noise_removes_celex():
    cleaned = strip_technical_noise(FALLBACK_INPUT)
    assert "CELEX:" not in cleaned
    assert "32016R0679" not in cleaned
    assert "Skip to main content" not in cleaned


def test_has_required_sections():
    assert has_required_sections("## Kort antwoord\nJa\n\n## Uitleg\nOmdat")
    assert not has_required_sections("Alleen platte tekst")


def test_ensure_layperson_sections_adds_missing_blocks():
    result = ensure_layperson_sections("Korte samenvatting zonder koppen.", "Mag ik cookies weigeren?")
    assert "## Kort antwoord" in result
    assert "## Uitleg" in result
    assert "## Wat dit voor u kan betekenen" in result


def test_is_weak_detects_boilerplate():
    assert is_weak_layperson_answer("Ik kan dit niet bevestigen op basis van de tekst.")
    assert is_weak_layperson_answer(BOILERPLATE) is True
    assert not is_weak_layperson_answer(
        "## Kort antwoord\nU hebt recht op compensatie bij lange vertraging.\n\n"
        "## Uitleg\nEU261 geeft passagiers rechten bij vertraging binnen Europa. "
        "De luchtvaartmaatschappij moet hulp bieden en soms een vaste vergoeding betalen."
    )


def test_replace_fallback_boilerplate():
    replaced = replace_fallback_boilerplate("Op basis of GDPR lijkt artikel 6 relevant voor u.")
    assert "lijkt artikel" not in replaced.lower()
    replaced2 = replace_fallback_boilerplate("De regels over - NL zijn relevant voor uw vraag.")
    assert "zijn relevant voor uw vraag" not in replaced2.lower()


def test_strip_removes_artikel_none():
    assert "None" not in strip_technical_noise("Artikel None is niet van toepassing.")


def test_is_weak_detects_article_pipe_dump():
    pipe_dump = (
        "## Kort antwoord\nDORA geldt voor financiële instellingen.\n\n"
        "## Uitleg\n| article | body |\n| 5 | DORA text |"
    )
    assert is_weak_layperson_answer(pipe_dump) is True


def test_is_weak_detects_duplicate_kort_antwoord():
    duplicate = "## Kort antwoord\nJa.\n\n## Kort antwoord\nNee.\n\n## Uitleg\nUitleg."
    assert is_weak_layperson_answer(duplicate) is True


def test_is_hybrid_boilerplate_detects_pipe_dump():
    from backend.src.utils.layperson_answer_formatter import is_hybrid_boilerplate

    pipe_dump = "## Kort antwoord\nDORA\n\n## Uitleg\n| article | body |"
    assert is_hybrid_boilerplate(pipe_dump) is True
    assert is_hybrid_boilerplate("## Kort antwoord\nJa, mag.\n\n## Uitleg\nNormale tekst.") is False
