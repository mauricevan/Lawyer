"""Tests for versioned prompt loader (plan7 P)."""
from shared.config.prompt_loader import (
    get_mode_hint,
    get_prompt_version,
    get_system_prompt,
    load_prompt_config,
)


def test_prompt_config_loads() -> None:
    config = load_prompt_config()
    assert "system_prompts" in config
    assert config["system_prompts"]["layperson"]


def test_get_system_prompt_professional() -> None:
    prompt = get_system_prompt("professional")
    assert "CELEX" in prompt or "celex" in prompt.lower()


def test_get_mode_hint_defaults_to_open() -> None:
    hint = get_mode_hint("unknown_mode", "layperson")
    assert hint == get_mode_hint("open", "layperson")


def test_prompt_version_set() -> None:
    assert get_prompt_version().startswith("2026")
