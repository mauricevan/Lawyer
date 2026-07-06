"""Tests for declarant uncertainty sections."""
from backend.src.utils.declarant_uncertainties import render_uncertainties_section


def test_customs_question_gets_uncertainties():
    section = render_uncertainties_section("Moet ik douaneaangifte doen voor pakketjes uit China?")
    assert section is not None
    assert "## Onzekerheden" in section
    assert "IOSS" in section


def test_identity_question_gets_uncertainties():
    section = render_uncertainties_section("moet ik me in de eu kunnen legitimeren")
    assert section is not None
    assert "EU-burger" in section
