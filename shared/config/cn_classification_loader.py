"""Load CN classification guidance from YAML."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CONFIG_PATH = Path(__file__).parent / "cn_classification.yaml"


@lru_cache(maxsize=1)
def load_cn_classification_config(path: Path | None = None) -> dict[str, Any]:
    source = path or _CONFIG_PATH
    with open(source, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def get_cn_positions() -> list[dict[str, Any]]:
    return list(load_cn_classification_config().get("positions", []))


def get_cn_referrals() -> list[dict[str, Any]]:
    return list(load_cn_classification_config().get("referrals", []))


def get_classification_signals() -> list[str]:
    return [str(s).lower() for s in load_cn_classification_config().get("classification_signals", [])]


def get_import_signals() -> list[str]:
    return [str(s).lower() for s in load_cn_classification_config().get("import_signals", [])]
