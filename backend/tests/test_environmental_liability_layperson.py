"""Layperson Dutch answers for environmental liability must stay relevant and in Dutch."""
from backend.src.services.chunk_quality_service import ChunkQualityService
from backend.src.services.layperson_clear_answer_composer import LaypersonClearAnswerComposer
from backend.src.utils.legal_chunk_text import matches_query_language

ENV_QUESTION = (
    "Welke verplichtingen legt de Europese Milieuaansprakelijkheidsrichtlijn "
    "op aan exploitanten die milieuschade veroorzaken?"
)
ENGLISH_RECITAL = {
    "celex": "32004L0035",
    "title": "EUR-Lex - 32004L0035 - EN",
    "article_number": "1",
    "text": (
        "CELEX:32004L0035 | L_2004142EN.01000101.xml | Artikel 1 | article\n"
        "(30) Failure to act could result in increased site contamination and "
        "greater loss of biodiversity in the future."
    ),
}
DUTCH_OPERATIVE = {
    "celex": "32004L0035",
    "title": "EUR-Lex - 32004L0035 - NL",
    "article_number": "4",
    "text": (
        "CELEX:32004L0035 | L_2004142NL.01000101.xml | Artikel 4 | article\n"
        "Artikel 4. Wanneer milieuschade is veroorzaakt of dreigt te worden veroorzaakt, "
        "neemt de exploitant onverwijld de nodige preventieve maatregelen. De exploitant "
        "is verplicht onmiddellijk de bevoegde autoriteiten in kennis te stellen en "
        "herstelmaatregelen te treffen voor de veroorzaakte milieuschade."
    ) * 2,
}


def test_english_chunks_rejected_for_dutch_query():
    service = ChunkQualityService()
    kept = service.filter_chunks([ENGLISH_RECITAL], expected_language="nl")
    assert kept == []
    assert not matches_query_language(ENGLISH_RECITAL["text"], "nl")


def test_dutch_operator_obligations_in_layperson_answer():
    composer = LaypersonClearAnswerComposer()
    answer = composer.compose_without_llm(ENV_QUESTION, [ENGLISH_RECITAL, DUTCH_OPERATIVE])
    assert answer
    lowered = answer.lower()
    assert "failure to act" not in lowered
    assert "this directive shall" not in lowered
    assert "exploitant" in lowered
    assert "milieuschade" in lowered
    assert answer.count("## Kort antwoord") == 1
    assert "## Wat betekent dit in de praktijk?" in answer
    assert "| Verplichting | Uitleg |" in answer
    kort_body = answer.split("## Wat betekent dit in de praktijk?")[0]
    assert "Ja." in kort_body
