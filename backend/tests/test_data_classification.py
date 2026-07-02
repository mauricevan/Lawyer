"""Tests for data classification map."""
from backend.src.security.data_classification import DataClass, classification_report


def test_users_classified_as_pii():
    report = classification_report()
    assert report["users"] == DataClass.PII.value


def test_documents_classified_as_non_pii():
    report = classification_report()
    assert report["documents"] == DataClass.NON_PII.value
