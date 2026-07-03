"""Automated failover scenario evaluation (plan14 AB)."""
import json
from pathlib import Path
from typing import Any

from backend.src.services.failover_simulation import apply_failover_scenario
from backend.src.services.rag_service import RagService
from backend.src.utils.failover_config import load_failover_policy
from shared.schemas.query import QueryRequest

_REPO = Path(__file__).resolve().parents[3]
_DEFAULT_FIXTURE = _REPO / "backend/tests/fixtures/failover_scenarios.json"


class FailoverEvalService:
    """Runs offline failover scenarios against simulated dependency loss."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path or _DEFAULT_FIXTURE

    def run(self) -> dict[str, Any]:
        scenarios = json.loads(self._fixture_path.read_text(encoding="utf-8"))
        results: list[dict[str, Any]] = []
        failures: list[str] = []
        for scenario in scenarios:
            outcome = self._run_scenario(scenario)
            results.append(outcome)
            failures.extend(outcome["errors"])
        gate = load_failover_policy().get("gate", {})
        min_pass = int(gate.get("min_pass_scenarios", len(scenarios)))
        passed_count = sum(1 for row in results if row["passed"])
        passed = not failures and passed_count >= min_pass
        return {
            "suite": "failover_eval",
            "passed": passed,
            "scenario_count": len(scenarios),
            "passed_count": passed_count,
            "failures": failures,
            "results": results,
        }

    async def _execute(self, scenario: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
        rag = RagService()
        apply_failover_scenario(rag, scenario)
        request = QueryRequest(question=scenario["question"], audience="professional")
        return await rag._retrieve(request)

    def _run_scenario(self, scenario: dict[str, Any]) -> dict[str, Any]:
        import asyncio

        chunks, route = asyncio.run(self._execute(scenario))
        errors = self._validate_scenario(scenario, chunks, route)
        return {
            "id": scenario["id"],
            "simulate": scenario.get("simulate"),
            "route": route,
            "chunk_count": len(chunks),
            "passed": not errors,
            "errors": errors,
        }

    def _validate_scenario(
        self,
        scenario: dict[str, Any],
        chunks: list[dict[str, Any]],
        route: str,
    ) -> list[str]:
        errors: list[str] = []
        scenario_id = scenario["id"]
        if expected := scenario.get("expect_route"):
            if route != expected:
                errors.append(f"{scenario_id}: route {route} != {expected}")
        if expected_in := scenario.get("expect_route_in"):
            if route not in expected_in:
                errors.append(f"{scenario_id}: route {route} not in {expected_in}")
        if scenario.get("expect_nonempty", True) and not chunks:
            errors.append(f"{scenario_id}: expected chunks, got none")
        if source := scenario.get("expect_source"):
            actual = chunks[0].get("source") if chunks else None
            if actual != source:
                errors.append(f"{scenario_id}: source {actual} != {source}")
        return errors
