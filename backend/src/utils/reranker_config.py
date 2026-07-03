"""Load reranker model variants from shared config."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_PATH = _REPO_ROOT / "shared/config/reranker_models.yaml"


@lru_cache(maxsize=1)
def load_reranker_config() -> dict[str, Any]:
    with open(_CONFIG_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def list_variants() -> list[str]:
    return list(load_reranker_config().get("variants", {}).keys())


def resolve_model_id(variant: str) -> str:
    variants = load_reranker_config().get("variants", {})
    if variant not in variants:
        known = ", ".join(sorted(variants))
        raise ValueError(f"Unknown reranker variant '{variant}'. Known: {known}")
    return str(variants[variant]["model_id"])


def experiment_thresholds() -> dict[str, float]:
    raw = load_reranker_config().get("experiment", {})
    return {
        "mrr_lift_min": float(raw.get("mrr_lift_min", 0.05)),
        "mrr_ceiling": float(raw.get("mrr_ceiling", 0.95)),
        "p95_retrieval_ms_max": float(raw.get("p95_retrieval_ms_max", 10000)),
        "recall_regression_max": float(raw.get("recall_regression_max", 0.01)),
    }
