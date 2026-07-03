#!/usr/bin/env python3
"""Run router intent eval fixture (plan12 AC)."""
import argparse
import json
from pathlib import Path

from backend.src.services.router_intent_eval_service import RouterIntentEvalService


def main() -> None:
    parser = argparse.ArgumentParser(description="Router intent eval")
    parser.add_argument("--fixture", type=Path, default=None)
    args = parser.parse_args()
    report = RouterIntentEvalService(fixture_path=args.fixture).run()
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(f"Router intent eval failed: {report['failures']}")


if __name__ == "__main__":
    main()
