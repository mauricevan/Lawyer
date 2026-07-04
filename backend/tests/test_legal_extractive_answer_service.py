"""Tests for extractive legal answers from chunks."""
from backend.src.services.legal_extractive_answer_service import LegalExtractiveAnswerService

Q = (
    "Kan de importeur terugbetaling van invoerrechten krijgen? "
    "De douanewaarde was te hoog door een niet-verwerkte korting."
)


def test_extractive_answer_from_ucc_chunk():
    chunks = [{
        "celex": "32013R0952",
        "article_number": "116",
        "title": "UCC",
        "text": (
            "CELEX:32013R0952 | L_2013269NL.01000101.xml | Artikel 116 | article "
            "Artikel 116 Algemene bepalingen 1. Onder de bij deze afdeling vastgestelde "
            "voorwaarden wordt overgegaan tot terugbetaling of kwijtschelding van bedragen "
            "aan invoer- of uitvoerrechten, om elk van de volgende redenen: a) invoer- of "
            "uitvoerrechten die te veel in rekening zijn gebracht."
        ),
    }]
    answer = LegalExtractiveAnswerService().build_layperson_answer(Q, chunks)
    assert answer is not None
    assert "terugbetaling" in answer.lower()
    assert "116" in answer
    assert "## Kort antwoord" in answer


def test_extractive_deadline_answer_from_article_121():
    chunks = [{
        "celex": "32013R0952",
        "article_number": "121",
        "title": "UCC",
        "text": (
            "Artikel 121 Termijnen 1. Verzoeken tot terugbetaling of kwijtschelding worden "
            "ingediend binnen een termijn van drie jaar vanaf de datum van heffing."
        ),
    }]
    question = "Binnen welke termijn moet ik een verzoek tot terugbetaling van douanerechten indienen?"
    answer = LegalExtractiveAnswerService().build_professional_answer(question, chunks)
    assert answer is not None
    assert "121" in answer
    assert "drie jaar" in answer.lower()
