#!/usr/bin/env python3
"""Readiness pass-rate SLO gate (plan14 KPI close)."""
import argparse
import asyncio
import json
import os

from backend.src.services.readiness_gate_service import ReadinessGateService


async def _run_live(service: ReadinessGateService, backend_url: str, samples: int) -> dict:
    probe_samples = await service.probe_live(backend_url, samples)
    return service.evaluate_samples(probe_samples, "live")


def main() -> None:
    parser = argparse.ArgumentParser(description="Readiness pass-rate gate")
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    service = ReadinessGateService()
    if args.simulate or os.getenv("CI") == "true":
        payload = service.simulate_report()
    else:
        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")
        payload = asyncio.run(_run_live(service, backend_url, args.samples))
    service.write_report(payload, service.report_path())
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Readiness pass-rate gate failed")


if __name__ == "__main__":
    main()
