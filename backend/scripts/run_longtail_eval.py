#!/usr/bin/env python3
"""Run long-tail retrieval eval with threshold gate (plan12 AD)."""
import argparse
import asyncio
import json
from datetime import date
from pathlib import Path

from backend.src.services.longtail_eval_service import LongtailEvalService

_REPO = Path(__file__).resolve().parents[2]
_REPORT_PATH = _REPO / "docs/data/eval-reports/longtail-latest.json"


async def main_async(fixture: Path | None, report_path: Path) -> None:
    result = await LongtailEvalService(fixture_path=fixture).run()
    payload = {
        "version": date.today().isoformat(),
        "suite": "longtail",
        **result,
    }
    print(json.dumps(payload, indent=2))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not result["passed"]:
        raise SystemExit(f"Long-tail eval failed: {result['failures']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run long-tail retrieval eval")
    parser.add_argument("--fixture", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=_REPORT_PATH)
    args = parser.parse_args()
    asyncio.run(main_async(args.fixture, args.report))


if __name__ == "__main__":
    main()
