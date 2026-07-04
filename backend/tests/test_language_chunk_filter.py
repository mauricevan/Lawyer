"""Language-aware chunk filtering for layperson answers."""
from backend.src.utils.legal_chunk_text import is_eurlex_placeholder_title, matches_query_language


def test_eurlex_placeholder_title_detected():
    assert is_eurlex_placeholder_title("EUR-Lex - 32004L0035 - NL")
    assert is_eurlex_placeholder_title("EUR-Lex - 32004L0035 - EN")
    assert not is_eurlex_placeholder_title("Richtlijn milieuaansprakelijkheid")


def test_matches_query_language_dutch_vs_english():
    dutch = "De exploitant is verplicht herstelmaatregelen te treffen voor milieuschade."
    english = "The operator shall take remedial measures where environmental damage occurs."
    assert matches_query_language(dutch, "nl")
    assert not matches_query_language(english, "nl")
    assert matches_query_language(english, "en")
