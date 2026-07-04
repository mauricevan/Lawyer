"""Tests for layperson topic YAML loader."""
from shared.config.layperson_topic_loader import get_layperson_topics, load_layperson_topic_config


def test_loader_merges_multi_file_topics():
    topics = get_layperson_topics()
    ids = {t["id"] for t in topics}
    assert len(topics) >= 80
    assert "flight_compensation" in ids
    assert "psd2_chargeback" in ids
    assert "platform_account_termination" in ids
    assert "spam_sms" in ids
    assert "bezorgdrone_registratie" in ids


def test_loader_has_no_duplicate_ids():
    topics = get_layperson_topics()
    ids = [t["id"] for t in topics]
    assert len(ids) == len(set(ids))


def test_config_has_version():
    config = load_layperson_topic_config()
    assert config.get("version")
