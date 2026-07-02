"""Load dataset registry for governance and lineage (plan7 N)."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

_REGISTRY_PATH = Path(__file__).parent / "dataset_registry.yaml"


@dataclass(frozen=True)
class DatasetEntry:
    dataset_id: str
    path: str
    version: str
    owner: str
    description: str = ""


@lru_cache(maxsize=1)
def load_dataset_registry(path: Path | None = None) -> dict[str, DatasetEntry]:
    source = path or _REGISTRY_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    output: dict[str, DatasetEntry] = {}
    for dataset_id, entry in data.get("datasets", {}).items():
        output[dataset_id] = DatasetEntry(
            dataset_id=dataset_id,
            path=entry["path"],
            version=entry["version"],
            owner=entry.get("owner", "engineering"),
            description=entry.get("description", ""),
        )
    return output


def get_registry_version(path: Path | None = None) -> str:
    source = path or _REGISTRY_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return str(data.get("version", "unknown"))
