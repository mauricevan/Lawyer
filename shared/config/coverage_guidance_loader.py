"""Load topic guidance for insufficient-coverage answers."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from shared.schemas.coverage_guidance import CoverageFramework, CoverageGuidance, CoverageReferral

_CONFIG_PATH = Path(__file__).parent / "coverage_guidance.yaml"


@lru_cache(maxsize=1)
def load_coverage_guidance_config(path: Path | None = None) -> dict[str, Any]:
    source = path or _CONFIG_PATH
    with open(source, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def get_coverage_topics() -> list[dict[str, Any]]:
    return list(load_coverage_guidance_config().get("topics", []))


def get_mismatch_config() -> dict[str, Any]:
    return dict(load_coverage_guidance_config().get("mismatch_intents", {}))


def get_topic_gate_exclude_patterns() -> list[str]:
    return [str(p).lower() for p in load_coverage_guidance_config().get("topic_gate_exclude_patterns", [])]


def topic_to_guidance(topic: dict[str, Any]) -> CoverageGuidance:
    return CoverageGuidance(
        topic_id=str(topic["id"]),
        sensitivity=topic.get("sensitivity", "low"),
        empathy_opener=str(topic.get("empathy_opener", "")),
        frameworks=[
            CoverageFramework(name=str(f["name"]), summary=str(f["summary"]))
            for f in topic.get("frameworks", [])
        ],
        referrals=[
            CoverageReferral(
                label=str(r["label"]),
                url=str(r["url"]),
                type=r["type"],
            )
            for r in topic.get("referrals", [])
        ],
    )
