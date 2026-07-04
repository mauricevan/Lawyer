"""Tests for classification context matching."""
from backend.src.utils.classification_context_match import (
    context_supports_classification,
    is_metadata_only_context,
)

HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)
METADATA_CHUNK = {
    "text": (
        "CELEX:31987R2658 Verordening 2658/87 tarief- en statistieknomenclatuur "
        "Publicatieblad Nr. L 256 blz. 0001 - 0675 Bijzondere uitgave EUR-Lex - "
        "Avis juridique important pour le document."
    ),
    "celex": "31987R2658",
}
LEGAL_CHUNK = {
    "text": (
        "0101 Paarden, ezels, muilezels en hetzelven, levend. "
        "0101 21 00 Fokdieren van zuiver ras. Andere paarden voor import."
    ) * 4,
    "celex": "31987R2658",
}


def test_metadata_does_not_support_classification():
    assert not context_supports_classification(HORSE_QUESTION, [METADATA_CHUNK])


def test_legal_chunk_supports_classification():
    assert context_supports_classification(HORSE_QUESTION, [LEGAL_CHUNK])


def test_is_metadata_only_context_detects_title_pages():
    assert is_metadata_only_context([METADATA_CHUNK])


def test_is_metadata_only_context_false_for_operative_text():
    assert not is_metadata_only_context([LEGAL_CHUNK])
