#!/usr/bin/env python3
"""EXP-002 reranker A/B eval — compare control vs candidate variant."""
import argparse
import asyncio
import json
from datetime import date
from pathlib import Path

from backend.src.services.reranker_eval_service import RerankerEvalService
from backend.src.services.reranker_experiment_service import RerankerExperimentService

_REPO = Path(__file__).resolve().parents[2]
_REPORT_PATH = _REPO / "docs/data/eval-reports/reranker-ab-latest.json"


async def run_ab(fixture: Path | None) -> dict:
    evaluator = RerankerEvalService(fixture_path=fixture)
    control = await evaluator.evaluate_variant("control")
    candidate = await evaluator.evaluate_variant("candidate")
    gate = RerankerExperimentService().evaluate_promotion_gate(control, candidate)
    return {
        "version": date.today().isoformat(),
        "experiment_id": "EXP-002",
        "passed": gate["passed"],
        "control": control,
        "candidate": candidate,
        "gate": gate,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EXP-002 reranker A/B eval")
    parser.add_argument("--fixture", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=_REPORT_PATH)
    args = parser.parse_args()
    report = asyncio.run(run_ab(args.fixture))
    print(json.dumps(report, indent=2))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["passed"]:
        raise SystemExit("EXP-002 gate failed — candidate not promoted")


if __name__ == "__main__":
    main()
