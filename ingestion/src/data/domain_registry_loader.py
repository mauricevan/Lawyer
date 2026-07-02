"""Load domain registry for routing, seeds, and go/no-go decisions."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml

DomainStatus = Literal["go", "pilot", "no_go"]

_REGISTRY_PATH = Path(__file__).parent / "domain_registry.yaml"


@dataclass(frozen=True)
class DomainConfig:
    domain_id: str
    label: str
    cluster: str
    keywords: tuple[str, ...]
    question_volume: str
    risk: str
    impact: str
    min_recall_at_5: float
    status: DomainStatus
    seed_celex: tuple[str, ...]


@lru_cache(maxsize=1)
def load_domain_registry(path: Path | None = None) -> dict[str, DomainConfig]:
    source = path or _REGISTRY_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    output: dict[str, DomainConfig] = {}
    for domain_id, entry in data.get("domains", {}).items():
        selection = entry.get("selection", {})
        benchmark = entry.get("benchmark", {})
        output[domain_id] = DomainConfig(
            domain_id=domain_id,
            label=entry["label"],
            cluster=entry["cluster"],
            keywords=tuple(entry.get("keywords", [])),
            question_volume=selection.get("question_volume", "low"),
            risk=selection.get("risk", "medium"),
            impact=selection.get("impact", "medium"),
            min_recall_at_5=float(benchmark.get("min_recall_at_5", 0.8)),
            status=entry.get("status", "pilot"),
            seed_celex=tuple(entry.get("seed_celex", [])),
        )
    return output


def get_domain_keywords() -> dict[str, tuple[str, ...]]:
    registry = load_domain_registry()
    return {domain_id: config.keywords for domain_id, config in registry.items()}


def resolve_domain_for_celex(celex: str) -> str | None:
    registry = load_domain_registry()
    for domain_id, config in registry.items():
        if celex in config.seed_celex:
            return domain_id
    from ingestion.src.data.curated_loader import load_documents_by_cluster

    for domain_id, config in registry.items():
        cluster_docs = load_documents_by_cluster(config.cluster)
        if any(doc.celex == celex for doc in cluster_docs):
            return domain_id
    return None
