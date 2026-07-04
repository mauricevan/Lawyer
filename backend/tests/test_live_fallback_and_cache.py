"""Tests for live fallback and in-memory retrieval cache."""
import pytest

from backend.src.services.retrieval_pipeline_service import RetrievalPipelineService
from shared.schemas.query import QueryRequest


class _FakeEmbeddings:
    def embed_query(self, _question: str) -> list[float]:
        return [0.1] * 8


class _FakeQdrantEmpty:
    def search(self, *args, **kwargs):
        return []

    def search_by_celex(self, *args, **kwargs):
        return []

    def search_with_language_fallback(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def search_by_celex_with_language_fallback(self, *args, **kwargs):
        return self.search_by_celex(*args, **kwargs)


class _FakeReranker:
    variant = "control"
    model_id = "test"
    last_latency_ms = 0.0

    def rerank(self, *args, **kwargs):
        return []


class _FakeRerankerLowScore:
    variant = "control"
    model_id = "test"
    last_latency_ms = 0.0

    def rerank(self, *args, **kwargs):
        return [{"chunk_id": "local:1", "score": 0.05, "text": "weak local"}]


class _FakeLive:
    async def fallback_chunks(
        self,
        question: str,
        language: str = "nl",
        celex_hint: str | None = None,
        is_celex_allowed=None,
    ):
        return [{
            "chunk_id": "live:32022R2554",
            "celex": "32022R2554",
            "title": "DORA",
            "text": (
                "Digitale operationele weerbaarheid voor financiële entiteiten met ICT-risico's. "
                "Financial entities shall maintain ICT risk management frameworks."
            ) * 3,
            "source": "live_fallback",
        }]


def _patch_pipeline(pipeline: RetrievalPipelineService, reranker: object) -> None:
    pipeline._embeddings = _FakeEmbeddings()
    pipeline._qdrant = _FakeQdrantEmpty()
    pipeline._reranker = reranker
    pipeline._live = _FakeLive()


@pytest.mark.asyncio
async def test_retrieve_uses_live_fallback_when_local_empty():
    pipeline = RetrievalPipelineService()
    _patch_pipeline(pipeline, _FakeReranker())
    request = QueryRequest(question="Wat zegt 32022R2554?", audience="professional")
    results, route, _ = await pipeline.retrieve(request, session=None)
    assert results
    assert results[0]["source"] == "live_fallback"
    assert route == "live_fallback"


@pytest.mark.asyncio
async def test_retrieve_uses_memory_cache_after_first_call():
    pipeline = RetrievalPipelineService()
    _patch_pipeline(pipeline, _FakeReranker())
    request = QueryRequest(question="Wat zegt 32022R2554?", audience="professional")
    first_chunks, first_route, _ = await pipeline.retrieve(request, session=None)
    second_chunks, second_route, _ = await pipeline.retrieve(request, session=None)
    assert first_chunks == second_chunks
    assert first_route == "live_fallback"
    assert second_route == "cache"


@pytest.mark.asyncio
async def test_retrieve_uses_live_fallback_for_low_score_results():
    pipeline = RetrievalPipelineService()
    _patch_pipeline(pipeline, _FakeRerankerLowScore())
    request = QueryRequest(question="Wat zegt 32022R2554?", audience="professional")
    results, route, _ = await pipeline.retrieve(request, session=None)
    assert results
    assert results[0]["source"] == "live_fallback"
    assert route == "live_fallback"


class _FakeRerankerIrrelevantHighScore:
    variant = "control"
    model_id = "test"
    last_latency_ms = 0.0

    def rerank(self, *args, **kwargs):
        return [{
            "chunk_id": "local:gdpr",
            "celex": "32016R0679",
            "title": "GDPR",
            "score": 0.45,
            "text": "Verwerking van persoonsgegevens door verwerkingsverantwoordelijken.",
        }]


HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)


@pytest.mark.asyncio
async def test_horse_classification_question_triggers_hint_live_fallback():
    pipeline = RetrievalPipelineService()
    _patch_pipeline(pipeline, _FakeRerankerIrrelevantHighScore())
    pipeline._live = _FakeLiveNomenclature()
    request = QueryRequest(question=HORSE_QUESTION, audience="layperson")
    results, route, _ = await pipeline.retrieve(request, session=None)
    assert results
    assert results[0]["celex"] == "31987R2658"
    assert route == "live_fallback"


class _FakeQdrantWithGn:
    def search(self, *args, **kwargs):
        return []

    def search_by_celex(self, celex_values, limit=12, language=None, in_force_only=True):
        return [{
            "chunk_id": "local:gn:1",
            "celex": "31987R2658",
            "title": "Gecombineerde Nomenclatuur",
            "text": (
                "0101 Paarden, ezels, muilezels en hetzelven, levend. "
                "0101 21 00 Fokdieren van zuiver ras. "
                "0101 29 Andere paarden voor import en douaneaangifte."
            ) * 4,
            "score": 0.82,
        }]

    def search_with_language_fallback(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def search_by_celex_with_language_fallback(self, celex_values, limit=12, language=None, in_force_only=True):
        return self.search_by_celex(celex_values, limit, language, in_force_only)


@pytest.mark.asyncio
async def test_usable_indexed_gn_chunks_skip_live_fallback():
    pipeline = RetrievalPipelineService()
    pipeline._embeddings = _FakeEmbeddings()
    pipeline._qdrant = _FakeQdrantWithGn()
    pipeline._reranker = _FakeRerankerIrrelevantHighScore()
    pipeline._live = _FakeLiveNomenclature()
    request = QueryRequest(question=HORSE_QUESTION, audience="layperson")
    results, route, _ = await pipeline.retrieve(request, session=None)
    assert results
    assert results[0]["celex"] == "31987R2658"
    assert route != "live_fallback"


class _FakeLiveNomenclature:
    async def fallback_chunks(
        self,
        question: str,
        language: str = "nl",
        celex_hint: str | None = None,
        is_celex_allowed=None,
    ):
        assert celex_hint == "31987R2658"
        return [{
            "chunk_id": "live:31987R2658",
            "celex": "31987R2658",
            "title": "Combined nomenclature",
            "text": "Gecombineerde Nomenclatuur douanetarief en tariefindeling EU.",
            "source": "live_fallback",
        }]


@pytest.mark.asyncio
async def test_oj_citation_2658_triggers_live_fallback():
    pipeline = RetrievalPipelineService()
    _patch_pipeline(pipeline, _FakeRerankerLowScore())
    pipeline._live = _FakeLiveNomenclature()
    question = "Ben je bekend met Verordening (EEG) nr. 2658/87?"
    request = QueryRequest(question=question, audience="layperson")
    results, route, _ = await pipeline.retrieve(request, session=None)
    assert results
    assert results[0]["celex"] == "31987R2658"
    assert route == "live_fallback"


class _FakeLiveCustomsCode:
    async def fallback_chunks(
        self,
        question: str,
        language: str = "nl",
        celex_hint: str | None = None,
        is_celex_allowed=None,
    ):
        assert celex_hint == "32013R0952"
        return [{
            "chunk_id": "live:32013R0952",
            "celex": "32013R0952",
            "title": "Union Customs Code",
            "text": "Douanewetboek van de Unie en douaneprocedures van de EU.",
            "source": "live_fallback",
        }]


@pytest.mark.asyncio
async def test_modern_oj_citation_952_2013_triggers_live_fallback():
    pipeline = RetrievalPipelineService()
    _patch_pipeline(pipeline, _FakeRerankerLowScore())
    pipeline._live = _FakeLiveCustomsCode()
    question = "Ben je bekend met Verordening (EU) nr. 952/2013?"
    request = QueryRequest(question=question, audience="layperson")
    results, route, _ = await pipeline.retrieve(request, session=None)
    assert results
    assert results[0]["celex"] == "32013R0952"
    assert route == "live_fallback"
