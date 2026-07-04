"""Tests for OJ citation → CELEX parsing."""
from ingestion.src.data.oj_citation_parser import parse_oj_celex


def test_oj_citation_2658_resolves_to_celex():
    assert parse_oj_celex("Verordening (EEG) nr. 2658/87") == "31987R2658"


def test_oj_citation_without_period_after_nr():
    assert parse_oj_celex("Verordening (EEG) nr 2658/87") == "31987R2658"


def test_oj_citation_familiarity_question():
    question = "Ben je bekend met Verordening (EEG) nr. 2658/87?"
    assert parse_oj_celex(question) == "31987R2658"


def test_explicit_celex_still_parsed():
    assert parse_oj_celex("Wat regelt CELEX 31987R2658?") == "31987R2658"


def test_directive_oj_uses_l_suffix():
    assert parse_oj_celex("Richtlijn 88/378") == "31988L0378"


def test_modern_regulation_number_year_resolves_to_celex():
    assert parse_oj_celex("Verordening (EU) nr. 952/2013") == "32013R0952"


def test_modern_regulation_year_number_resolves_to_celex():
    assert parse_oj_celex("Verordening (EU) 2016/679") == "32016R0679"


def test_modern_familiarity_question_customs_code():
    question = "Ben je bekend met Verordening (EU) nr. 952/2013?"
    assert parse_oj_celex(question) == "32013R0952"
