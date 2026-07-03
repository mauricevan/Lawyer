#!/usr/bin/env python3
"""Validate deprecation register against domain no_go seeds (plan13 AC)."""
import json
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]
_REGISTER = _REPO / "shared/config/document_deprecation_register.yaml"
_DOMAIN_REGISTRY = _REPO / "ingestion/src/data/domain_registry.yaml"

sys.path.insert(0, str(_REPO))
from backend.src.utils.document_deprecation_config import validate_register_payload


def _registered_celex(register: dict) -> set[str]:
    return {entry["celex"] for entry in register.get("entries", [])}


def _no_go_seed_celex(domain_registry: dict) -> set[str]:
    seeds: set[str] = set()
    for config in domain_registry.get("domains", {}).values():
        if config.get("status") != "no_go":
            continue
        for celex in config.get("seed_celex", []):
            seeds.add(celex)
    return seeds


def main() -> None:
    register = yaml.safe_load(_REGISTER.read_text(encoding="utf-8"))
    domain_registry = yaml.safe_load(_DOMAIN_REGISTRY.read_text(encoding="utf-8"))
    schema_errors = validate_register_payload(register)
    registered = _registered_celex(register)
    missing = sorted(_no_go_seed_celex(domain_registry) - registered)
    payload = {
        "suite": "deprecation_register",
        "passed": not schema_errors and not missing,
        "registered_count": len(registered),
        "schema_errors": schema_errors,
        "missing_no_go_seeds": missing,
    }
    print(json.dumps(payload, indent=2))
    if schema_errors:
        raise SystemExit(f"Deprecation register schema errors: {schema_errors}")
    if missing:
        raise SystemExit(f"Missing deprecation entries for no_go seeds: {missing}")


if __name__ == "__main__":
    main()
