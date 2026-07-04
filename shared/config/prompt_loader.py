"""Load versioned prompt configuration (plan7 P)."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CONFIG_PATH = Path(__file__).parent / "prompts.yaml"


@lru_cache(maxsize=1)
def load_prompt_config(path: Path | None = None) -> dict[str, Any]:
    source = path or _CONFIG_PATH
    with open(source, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def get_prompt_version() -> str:
    return str(load_prompt_config().get("version", "unknown"))


def get_system_prompt(audience: str, *, specific: bool = False) -> str:
    config = load_prompt_config()
    if specific:
        specific_key = "specific_professional" if audience == "professional" else "specific_layperson"
        if specific_key in config.get("system_prompts", {}):
            return str(config["system_prompts"][specific_key]).strip()
    key = "professional" if audience == "professional" else "layperson"
    return str(config["system_prompts"][key]).strip()


def get_mode_hint(mode: str, audience: str, *, specific: bool = False) -> str:
    config = load_prompt_config()
    bucket = "professional" if audience == "professional" else "layperson"
    hints = config["mode_hints"][bucket]
    if specific and "specific" in hints:
        return str(hints["specific"])
    return str(hints.get(mode, hints["open"]))


def get_follow_up_hint() -> str:
    return str(load_prompt_config().get("follow_up_hint", "")).strip()


def get_history_window() -> int:
    return int(load_prompt_config().get("history_window", 10))


def get_legal_planner_system_prompt() -> str:
    return str(load_prompt_config().get("legal_planner_system", "")).strip()


def get_legal_planner_user_template() -> str:
    return str(load_prompt_config().get("legal_planner_user_template", "")).strip()


def get_citation_verifier_system_prompt() -> str:
    return str(load_prompt_config().get("citation_verifier_system", "")).strip()
