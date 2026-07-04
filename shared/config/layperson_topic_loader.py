"""Load layperson topic guidance from multi-file YAML."""
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_TOPICS_DIR = Path(__file__).parent / "layperson_topics"
_LEGACY_PATH = Path(__file__).parent / "layperson_topic_guidance.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _validate_topic_patterns(topic: dict[str, Any]) -> None:
    """Log when broad patterns lack exclude_patterns or min_pattern_hits."""
    patterns = [str(p) for p in topic.get("patterns", [])]
    short = [p for p in patterns if len(p.split()) <= 2]
    if not short:
        return
    excludes = topic.get("exclude_patterns", [])
    min_hits = int(topic.get("min_pattern_hits", 1))
    if len(excludes) < 3 or min_hits < 2:
        topic_id = topic.get("id", "?")
        logger.warning(
            "Topic '%s' has broad patterns %s; prefer min_pattern_hits>=2 and >=3 exclude_patterns",
            topic_id,
            short[:3],
        )


def _merge_topic_files(directory: Path) -> list[dict[str, Any]]:
    topics: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for path in sorted(directory.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        for topic in _load_yaml(path).get("topics", []):
            topic_id = str(topic.get("id", ""))
            if not topic_id:
                continue
            if topic_id in seen_ids:
                raise ValueError(f"Duplicate layperson topic id: {topic_id}")
            _validate_topic_patterns(topic)
            seen_ids.add(topic_id)
            topics.append(topic)
    return topics


@lru_cache(maxsize=1)
def load_layperson_topic_config(path: Path | None = None) -> dict[str, Any]:
    if path is not None:
        return _load_yaml(path)
    if _TOPICS_DIR.is_dir() and any(_TOPICS_DIR.glob("[!_]*.yaml")):
        meta = _load_yaml(_TOPICS_DIR / "_meta.yaml")
        return {"version": meta.get("version", ""), "topics": _merge_topic_files(_TOPICS_DIR)}
    return _load_yaml(_LEGACY_PATH)


def get_layperson_topics() -> list[dict[str, Any]]:
    return list(load_layperson_topic_config().get("topics", []))
