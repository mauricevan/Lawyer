"""Tests for layperson clear answer markdown renderer."""
from backend.src.utils.layperson_clear_markdown import render_clear_answer
from shared.schemas.layperson_clear_answer import (
    ArticleSummary,
    LaypersonClearAnswer,
    ObligationRow,
    OfficialExcerpt,
    TermDefinition,
)


def test_render_section_order():
    answer = LaypersonClearAnswer(
        kort_antwoord="Ja. De richtlijn verplicht exploitanten om milieuschade te beperken.",
        obligations=[ObligationRow(label="Melden", uitleg="Informeer de autoriteit.")],
        voorbeeld="Een bedrijf lekt stoffen in een rivier.",
        juridische_basis=[ArticleSummary(article="5", title="Preventie", uitleg_nl="Neem maatregelen.")],
        begrippen=[TermDefinition(term="exploitant", definition_nl="De verantwoordelijke onderneming.")],
        let_op="De lidstaten stellen de uitvoering vast.",
        official_excerpts=[OfficialExcerpt(article="5", text="De exploitant neemt maatregelen.")],
    )
    md = render_clear_answer(answer)
    assert md.index("## Kort antwoord") < md.index("## Wat betekent dit in de praktijk?")
    assert md.index("## Wat betekent dit in de praktijk?") < md.index("## Voorbeeld")
    assert md.index("## Voorbeeld") < md.index("## Juridische basis")
    assert md.index("## Juridische basis") < md.index("## Officiële tekst")
    assert "<details>" in md
    assert md.index("## Officiële tekst") < md.index("## Begrippen")
    assert md.index("## Begrippen") < md.index("## Let op")


def test_obligations_table_markdown():
    answer = LaypersonClearAnswer(
        kort_antwoord="Ja.",
        obligations=[
            ObligationRow(label="Herstellen", uitleg="Herstel milieuschade."),
        ],
    )
    md = render_clear_answer(answer)
    assert "## Wat betekent dit in de praktijk?\n\n| Verplichting | Uitleg |" in md
    assert "| Verplichting | Uitleg |" in md
    assert "| Herstellen | Herstel milieuschade. |" in md
