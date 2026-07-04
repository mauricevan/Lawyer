#!/usr/bin/env python3
"""Lightweight query load test for plan3 validation."""
import argparse
import asyncio
import statistics
import time

import httpx

DEFAULT_URL = "http://127.0.0.1:8001/api/v1/query"
SAMPLE_QUESTIONS = (
    "Wat is DORA?",
    "Wat is CSRD?",
    "Wat zijn high-risk AI systemen?",
    "Wat zegt GDPR over consent?",
    "Wat is MiFID?",
    "Moet ik mijn chatbot registreren bij de overheid?",
    "Geldt de AI-wet ook voor mijn kleine webshop?",
    "Mag ik klantgegevens gebruiken om mijn AI te trainen?",
)


async def run_load(base_url: str, concurrency: int, requests_count: int) -> dict[str, float]:
    latencies: list[float] = []
    errors = 0
    semaphore = asyncio.Semaphore(concurrency)

    async def one_request(client: httpx.AsyncClient, question: str) -> None:
        nonlocal errors
        async with semaphore:
            started = time.perf_counter()
            try:
                response = await client.post(
                    base_url,
                    json={"question": question, "language": "nl", "audience": "professional"},
                    timeout=120.0,
                )
                if response.status_code >= 500:
                    errors += 1
            except Exception:
                errors += 1
            latencies.append((time.perf_counter() - started) * 1000)

    async with httpx.AsyncClient() as client:
        tasks = [
            one_request(client, SAMPLE_QUESTIONS[i % len(SAMPLE_QUESTIONS)])
            for i in range(requests_count)
        ]
        await asyncio.gather(*tasks)

    latencies.sort()
    return {
        "requests": float(requests_count),
        "errors": float(errors),
        "p50_ms": latencies[len(latencies) // 2] if latencies else 0.0,
        "p95_ms": latencies[int(len(latencies) * 0.95) - 1] if latencies else 0.0,
        "avg_ms": statistics.mean(latencies) if latencies else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Query load test")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--requests", type=int, default=20)
    args = parser.parse_args()
    summary = asyncio.run(run_load(args.url, args.concurrency, args.requests))
    print(summary)


if __name__ == "__main__":
    main()
