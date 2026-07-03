"""Tests for long-tail eval fixture and gate logic."""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.longtail_eval_service import LongtailEvalService

_REPO = Path(__file__).resolve().parents[2]
_FIXTURE = _REPO / "backend/tests/fixtures/rag_eval_longtail.json"


def test_longtail_fixture_exists_with_categories() -> None:
    if not _FIXTURE.is_file():
        subprocess.run(
            [sys.executable, str(_REPO / "backend/scripts/build_longtail_eval_fixture.py")],
            check=True,
            cwd=_REPO,
        )
    items = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    assert len(items) >= 15
    assert all(item.get("category") for item in items)
    assert all(item.get("expected_celex") for item in items)


def test_longtail_eval_script_exists() -> None:
    assert (_REPO / "scripts/qa/run-longtail-eval.sh").is_file()


def test_threshold_failures_detect_recall_regression() -> None:
    service = LongtailEvalService()
    failures = service._threshold_failures({"recall_at_5": 0.5, "mrr": 0.8, "count": 10.0})
    assert any("recall_at_5" in item for item in failures)


@pytest.mark.asyncio
async def test_longtail_eval_passes_with_perfect_retrieval() -> None:
    if not _FIXTURE.is_file():
        subprocess.run(
            [sys.executable, str(_REPO / "backend/scripts/build_longtail_eval_fixture.py")],
            check=True,
            cwd=_REPO,
        )
    items = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    service = LongtailEvalService(fixture_path=_FIXTURE)

    async def mock_retrieve(request):
        for item in items:
            if item["question"] == request.question:
                chunks = [{"celex": c, "chunk_id": c, "score": 0.9} for c in item["expected_celex"]]
                return chunks, "hybrid"
        return [], "local"

    with patch("backend.src.services.longtail_eval_service.RagService") as mock_rag:
        instance = mock_rag.return_value
        instance._route_request.side_effect = lambda req: req
        instance._retrieve = AsyncMock(side_effect=mock_retrieve)
        result = await service.run()
    assert result["passed"] is True
    assert result["summary"]["recall_at_5"] == 1.0
