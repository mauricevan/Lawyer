"""Unit tests for rule-based query routing."""
from backend.src.services.query_router_service import QueryRouterService
from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest


def test_router_extracts_domain_doc_type_and_celex():
    router = QueryRouterService()
    route = router.route(
        "Welke verplichtingen uit verordening 32022R2554 gelden nu voor banken?",
        "nl",
    )
    assert "finance" in route.domains
    assert "regulation" in route.doc_types
    assert route.celex_hint == "32022R2554"
    assert route.time_context == "current"


def test_router_detects_historical_context():
    router = QueryRouterService()
    route = router.route("Wat was historisch de oude versie van CSRD?", "nl")
    assert route.time_context == "historical"
    assert "sustainability" in route.domains


def test_rag_service_merges_router_output_into_filters():
    rag = RagService()
    request = QueryRequest(
        question="Toon de regels van DORA voor banken",
        audience="professional",
    )
    routed = rag._route_request(request)
    assert routed.filters is not None
    assert routed.filters.domain == "finance"
    assert routed.filters.celex == "32022R2554"
    assert routed.filters.time_context == "current"
