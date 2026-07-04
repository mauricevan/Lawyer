"""Tests for human-readable layperson prose from legal excerpts."""
from backend.src.services.legal_extractive_generic import build_generic_layperson
from backend.src.utils.legal_chunk_text import is_metadata_dump

QUESTION = (
    "Welke verplichtingen heeft een fabrikant wanneer een product een veiligheidsrisico "
    "blijkt te vormen volgens Verordening (EU) 2023/988?"
)
PIPE_RECITAL_CHUNK = {
    "celex": "32023R0988",
    "title": "L_2023135EN.01000101.xml",
    "article_number": "114",
    "text": (
        "| L_2023135EN.01000101.xml | section . "
        "(30) Together with the adaptation of Regulation (EU) No 1025/2012, a specific "
        "procedure for the adoption of the specific safety requirements should be introduced."
    ),
}
OPERATIVE_NL = {
    "celex": "32023R0988",
    "title": "GPSR",
    "article_number": "9",
    "text": (
        "Wanneer een product een risico vormt, stelt de fabrikant onverwijld de bevoegde "
        "autoriteiten op de hoogte. De fabrikant neemt corrigerende maatregelen en waarschuwt "
        "consumenten zonder onnodige vertraging. De fabrikant werkt samen met de markttoezichtautoriteiten."
    ),
}
OPERATIVE_EN = {
    "celex": "32023R0988",
    "title": "GPSR",
    "article_number": "10",
    "text": (
        "Manufacturers shall immediately inform the competent authorities when a product "
        "presents a risk. They shall take corrective action to eliminate the risk and "
        "cooperate with the authorities on any measures taken."
    ),
}


def test_metadata_dump_detects_pipe_recital():
    assert is_metadata_dump(PIPE_RECITAL_CHUNK["text"])


def test_build_layperson_ignores_pipe_recital_and_uses_operative_text():
    answer = build_generic_layperson(QUESTION, [PIPE_RECITAL_CHUNK, OPERATIVE_NL, OPERATIVE_EN])
    assert answer
    lowered = answer.lower()
    assert answer.count("## Kort antwoord") == 1
    assert "together with the adaptation" not in lowered
    assert ".xml" not in lowered
    assert "| section" not in lowered
    assert "artikel —" not in lowered
    assert "fabrikant" in lowered
    assert "**Artikel 9**" in answer or "**Artikel 10**" in answer
    assert len(answer.split("## Uitleg")[1]) > 200
