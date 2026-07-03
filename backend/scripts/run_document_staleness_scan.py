#!/usr/bin/env python3
"""Scan document index staleness against lifecycle policy (plan13 AA)."""
import argparse
import asyncio
import json
from pathlib import Path

from backend.src.database import SessionLocal
from backend.src.services.document_staleness_service import DocumentStalenessService

_REPO = Path(__file__).resolve().parents[2]


def _serialize_records(records) -> list[dict]:
    return [
        {
            "celex": row.celex,
            "language": row.language,
            "status": row.status,
            "indexed_at": row.indexed_at.isoformat() if row.indexed_at else None,
            "modified_at": row.modified_at.isoformat() if row.modified_at else None,
            "index_age_hours": row.index_age_hours,
            "modified_drift_hours": row.modified_drift_hours,
        }
        for row in records
        if row.status != "fresh"
    ]


async def run_scan(report_path: Path) -> dict:
    service = DocumentStalenessService()
    async with SessionLocal() as session:
        records = await service.scan(session)
    summary = service.summarize(records)
    gate = service.evaluate_gates(summary)
    payload = {
        "suite": "document_staleness",
        "passed": gate["passed"],
        "summary": summary,
        "gate": gate,
        "issues": _serialize_records(records),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Document staleness scan")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    report = args.report or (_REPO / DocumentStalenessService.report_path())
    payload = asyncio.run(run_scan(report))
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit(f"Staleness gate failed: {payload['gate']['failures']}")


if __name__ == "__main__":
    main()
