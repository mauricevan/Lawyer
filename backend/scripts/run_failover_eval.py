#!/usr/bin/env python3
"""Run offline failover scenario eval (plan14 AB)."""
import argparse
import json
from pathlib import Path

from backend.src.services.failover_eval_service import FailoverEvalService
from backend.src.utils.failover_config import failover_report_path

_REPO = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Failover scenario eval")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    report = args.report or (_REPO / failover_report_path())
    payload = FailoverEvalService().run()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit(f"Failover eval failed: {payload['failures']}")


if __name__ == "__main__":
    main()
