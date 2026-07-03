"""Evaluate router intent library against fixture cases."""
import json
from pathlib import Path
from typing import Any

from backend.src.services.query_router_service import QueryRouterService

_REPO = Path(__file__).resolve().parents[3]
_DEFAULT_FIXTURE = _REPO / "backend/tests/fixtures/router_intent_eval.json"


class RouterIntentEvalService:
    """Runs router intent eval cases from JSON fixture."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path or _DEFAULT_FIXTURE
        self._router = QueryRouterService()

    def run(self) -> dict[str, Any]:
        cases = json.loads(self._fixture_path.read_text(encoding="utf-8"))
        failures: list[str] = []
        for index, case in enumerate(cases):
            route = self._router.route(case["question"], "nl")
            failures.extend(self._validate_case(index, case, route))
        return {"passed": not failures, "count": len(cases), "failures": failures}

    def _validate_case(self, index: int, case: dict[str, Any], route) -> list[str]:
        errors: list[str] = []
        prefix = f"case[{index}]"
        if expected_intent := case.get("expected_intent"):
            if route.intent_id != expected_intent:
                errors.append(f"{prefix}: intent {route.intent_id} != {expected_intent}")
        if expected_domain := case.get("expected_domain"):
            if expected_domain not in route.domains:
                errors.append(f"{prefix}: domain {route.domains} missing {expected_domain}")
        if min_conf := case.get("min_confidence"):
            if route.confidence < float(min_conf):
                errors.append(f"{prefix}: confidence {route.confidence} < {min_conf}")
        if max_conf := case.get("max_confidence"):
            if route.confidence > float(max_conf):
                errors.append(f"{prefix}: confidence {route.confidence} > {max_conf}")
        if case.get("expect_no_domain_lock") and route.domains:
            errors.append(f"{prefix}: expected no domain lock, got {route.domains}")
        if expected_time := case.get("expected_time_context"):
            if route.time_context != expected_time:
                errors.append(f"{prefix}: time_context {route.time_context} != {expected_time}")
        if expected_cluster := case.get("expect_cluster"):
            if route.domain_cluster != expected_cluster:
                errors.append(f"{prefix}: cluster {route.domain_cluster} != {expected_cluster}")
        return errors
