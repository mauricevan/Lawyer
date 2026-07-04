"""Regression: GPSR manufacturer question must not show recital boilerplate."""
import asyncio

from backend.src.services.agent_answer_service import AgentAnswerService
from backend.src.services.layperson_clear_answer_composer import LaypersonClearAnswerComposer
from backend.src.services.layperson_answer_service import LaypersonAnswerService

QUESTION = (
    "Welke verplichtingen heeft een fabrikant wanneer een product een veiligheidsrisico "
    "blijkt te vormen volgens Verordening (EU) 2023/988 inzake algemene productveiligheid?"
)
PIPE_RECITAL_CHUNK = {
    "celex": "32023R0988",
    "title": "L_2023135EN.01000101.xml",
    "article_number": "114",
    "text": (
        "| L_2023135EN.01000101.xml | section . "
        "(30) Together with the adaptation of Regulation (EU) No 1025/2012."
    ),
}
OPERATIVE_CHUNK = {
    "celex": "32023R0988",
    "title": "GPSR",
    "article_number": "9",
    "text": (
        "Wanneer een product een risico vormt, stelt de fabrikant onverwijld de bevoegde "
        "autoriteiten op de hoogte en neemt corrigerende maatregelen. De fabrikant werkt "
        "samen met de autoriteiten en waarschuwt consumenten zonder onnodige vertraging."
    ) * 2,
}


def test_extractive_skips_recital_and_uses_manufacturer_obligations():
    chunks = [PIPE_RECITAL_CHUNK, OPERATIVE_CHUNK]
    answer = LaypersonClearAnswerComposer().compose_without_llm(QUESTION, chunks, allow_topic=False)
    assert answer
    lowered = answer.lower()
    assert "european commission" not in lowered
    assert "thereof" not in lowered
    assert "fabrikant" in lowered
    assert answer.count("## Kort antwoord") == 1


def test_layperson_format_does_not_duplicate_sections():
    chunks = [PIPE_RECITAL_CHUNK, OPERATIVE_CHUNK]
    raw = LaypersonClearAnswerComposer().compose_without_llm(QUESTION, chunks, allow_topic=False)
    assert raw
    formatted = LaypersonAnswerService().format(raw, QUESTION, chunks)
    assert formatted.count("## Kort antwoord") == 1
    assert "european commission" not in formatted.lower()


def test_agent_improve_layperson_replaces_weak_llm_output():
    service = AgentAnswerService()
    weak_llm = (
        "## Kort antwoord\nDe regels over L_2023135EN.01000101.xml zijn relevant.\n\n"
        "## Uitleg\nArticle 114 thereof, from the European Commission\n\n"
        "## Wat dit voor u kan betekenen\nLees de samenvatting hierboven."
    )
    from shared.schemas.query import QueryRequest

    request = QueryRequest(question=QUESTION, audience="layperson", language="nl")
    improved = asyncio.run(
        service._improve_layperson_answer(request, [PIPE_RECITAL_CHUNK, OPERATIVE_CHUNK], weak_llm)
    )
    assert improved.count("## Kort antwoord") == 1
    assert "fabrikant" in improved.lower()
    assert "samenvatting hierboven" not in improved.lower()
    assert "european commission" not in improved.lower()
