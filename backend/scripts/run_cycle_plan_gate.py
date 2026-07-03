#!/usr/bin/env python3
"""Cycle plan gate runner (plan16–plan30)."""
import argparse
import json
import sys

from backend.src.services.cycle_plan_gate_service import CyclePlanGateService

_REPO = CyclePlanGateService()._root  # noqa: SLF001 — script entrypoint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default=None, help="e.g. plan16")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    service = CyclePlanGateService()
    if args.all:
        payload = service.audit_all()
        report = _REPO / "docs/data/governance-reports/cycle-plans-latest.json"
    else:
        if not args.plan:
            raise SystemExit("Provide --plan plan16 or --all")
        payload = service.audit_plan(args.plan)
        report = _REPO / f"docs/data/governance-reports/{args.plan}-gate-latest.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit(f"Cycle plan gate failed: {args.plan or 'all'}")


if __name__ == "__main__":
    main()
