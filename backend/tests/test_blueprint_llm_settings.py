"""Blueprint-aligned LLM settings."""
from backend.src.config import settings


def test_llm_temperature_within_blueprint_limit():
    assert settings.llm_temperature <= 0.2


def test_llm_max_tokens_matches_blueprint_default():
    assert settings.llm_max_tokens == 1500
