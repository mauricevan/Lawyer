#!/usr/bin/env python3
"""Scan curated and indexed version conflicts (plan13 AD)."""
import argparse
import asyncio
import json
from pathlib import Path

from backend.src.database import SessionLocal
from backend.src.services.document_version_conflict_service import DocumentVersionConflictService
from backend.src.utils.document_version_config import version_gate_policy, version_report_path

_REPO = Path(__file__).resolve().parents[2]


async def run_scan(report_path: Path, curated_only: bool) -> dict:
    service = DocumentVersionConflictService()
    registration = service.validate_registered_families()
    curated_conflicts = service.scan_curated()
    indexed_conflicts: list = []
    if not curated_only:
        async with SessionLocal() as session:
            indexed_conflicts = await service.scan_indexed(session)
    gate = version_gate_policy()
    max_conflicts = int(gate.get("max_indexed_conflicts", 10))
    conflict_count = len(indexed_conflicts) if indexed_conflicts else len(curated_conflicts)
    passed = registration["passed"] and conflict_count <= max_conflicts
    payload = {
        "suite": "version_conflicts",
        "passed": passed,
        "registration": registration,
        "curated_conflicts": service.summarize(curated_conflicts),
        "indexed_conflicts": service.summarize(indexed_conflicts),
        "gate": {"max_indexed_conflicts": max_conflicts},
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Version conflict scan")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--curated-only", action="store_true")
    args = parser.parse_args()
    report = args.report or (_REPO / version_report_path())
    payload = asyncio.run(run_scan(report, args.curated_only))
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit("Version conflict gate failed")


if __name__ == "__main__":
    main()
