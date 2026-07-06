#!/usr/bin/env python3
"""Run the 8-question declarant acceptance suite (plan §4B)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.tests.acceptance.declarant_assertions import (
    DeclarantExpectation,
    assert_declarant_answer,
)

BASE = "http://localhost:8000/api/v1"

SCENARIOS: list[tuple[str, str, DeclarantExpectation]] = [
    (
        "q1_email_marketing",
        "Mag mijn werkgever mijn e-mailadres doorgeven aan een reclamebedrijf?",
        DeclarantExpectation(
            scenario_id="q1_email_marketing",
            required_celex=frozenset({"32016R0679"}),
            required_article_markers=frozenset({"artikel 6", "art. 6"}),
        ),
    ),
    (
        "q2_gpsr_recall",
        "Ik heb een webshop met speelgoed. Wanneer moet ik een product terugroepen?",
        DeclarantExpectation(
            scenario_id="q2_gpsr_recall",
            required_celex=frozenset({"32023R0988"}),
            required_article_markers=frozenset({"artikel 9", "art. 9", "artikel 31", "art. 31"}),
        ),
    ),
    (
        "q3_consumer_withdrawal",
        "Ik heb online schoenen gekocht maar ze passen niet. Hoe lang mag ik wachten met terugsturen?",
        DeclarantExpectation(
            scenario_id="q3_consumer_withdrawal",
            required_celex=frozenset({"32011L0083"}),
            required_article_markers=frozenset({"artikel 9", "art. 9"}),
            required_text_snippets=frozenset({"14 dagen"}),
        ),
    ),
    (
        "q4_customs_union",
        "Welke lidstaten maken deel uit van het douanegebied van de douane-unie?",
        DeclarantExpectation(
            scenario_id="q4_customs_union",
            required_celex=frozenset({"32013R0952", "12016E028"}),
            require_all_celex=True,
            required_article_markers=frozenset({"artikel 4", "artikel 28"}),
        ),
    ),
    (
        "q5_customs_china",
        (
            "Ik verkoop via webshop kleine pakketjes vanuit China naar NL onder 150 euro. "
            "Moet ik douaneaangifte doen?"
        ),
        DeclarantExpectation(
            scenario_id="q5_customs_china",
            required_celex=frozenset({"32013R0952"}),
            required_article_markers=frozenset({"artikel", "art."}),
        ),
    ),
    (
        "q6_vague_customs",
        "Moet ik douaneaangifte doen?",
        DeclarantExpectation(
            scenario_id="q6_vague_customs",
            require_adequate=False,
            require_sections=(),
            require_article_ref=False,
        ),
    ),
    (
        "q7_identity",
        "Moet ik me legitimeren bij een EU-overheidsdienst?",
        DeclarantExpectation(
            scenario_id="q7_identity",
            required_celex=frozenset({"32004L0038", "32014R0910"}),
            require_national_boundary=True,
        ),
    ),
    (
        "q8_gpsr_supplier",
        "Mag mijn werkgever van mij GPSR-documenten van de leverancier eisen?",
        DeclarantExpectation(
            scenario_id="q8_gpsr_supplier",
            required_celex=frozenset({"32023R0988"}),
            required_article_markers=frozenset({"artikel", "art."}),
        ),
    ),
]


async def _create_conv(client: httpx.AsyncClient) -> str:
    response = await client.post(f"{BASE}/conversations", json={"query_mode": "open"})
    response.raise_for_status()
    return response.json()["id"]


async def _query(client: httpx.AsyncClient, conv_id: str, question: str) -> dict:
    payload = {
        "question": question,
        "conversation_id": conv_id,
        "audience": "layperson",
        "language": "nl",
        "query_mode": "open",
    }
    response = await client.post(f"{BASE}/query", json=payload, timeout=600.0)
    response.raise_for_status()
    body = response.json()
    return {
        "answer": body.get("answer", ""),
        "coverage_status": body.get("coverage_status", ""),
        "retrieval_route": body.get("retrieval_route", ""),
        "verification_questions": body.get("verification_questions", []),
        "clarification_prompt": body.get("clarification_prompt"),
        "_chunks": [
            {"celex": cite.get("celex", "")}
            for cite in body.get("citations", [])
            if cite.get("celex")
        ],
    }


def _chunk_celexes(detail: dict) -> set[str]:
    chunks = detail.get("_chunks") or detail.get("retrieval_chunks") or []
    return {str(c.get("celex", "")) for c in chunks if c.get("celex")}


async def main() -> int:
    failures: list[str] = []
    async with httpx.AsyncClient() as client:
        health = await client.get("http://localhost:8000/health")
        if health.status_code != 200:
            print("FAIL: backend not reachable on :8000")
            return 1

        for scenario_id, question, expectation in SCENARIOS:
            conv_id = await _create_conv(client)
            detail = await _query(client, conv_id, question)
            answer = detail.get("answer", "")
            status = detail.get("coverage_status", "")
            celexes = _chunk_celexes(detail)

            if scenario_id == "q6_vague_customs":
                if status != "clarify_only":
                    failures.append(f"{scenario_id}: expected clarify_only, got {status}")
                elif not detail.get("verification_questions") and not detail.get("clarification_prompt"):
                    failures.append(f"{scenario_id}: clarify without chips/questions")
            else:
                failures.extend(
                    assert_declarant_answer(
                        scenario_id, answer, status, celexes, expectation,
                    )
                )

            route = detail.get("retrieval_route", "")
            mark = "PASS" if not any(f.startswith(scenario_id) for f in failures) else "FAIL"
            print(f"{mark} {scenario_id} status={status} route={route} celex={sorted(celexes)}")
            if mark == "FAIL":
                print(f"  answer preview: {answer[:200].replace(chr(10), ' ')}...")

    if failures:
        print("\nFailures:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("\n8/8 declarant acceptance PASS")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
