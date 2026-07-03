"""Unit tests for rule-based query routing and intent library."""
from backend.src.services.query_router_service import QueryRouterService
from backend.src.services.rag_service import RagService
from backend.src.services.router_intent_eval_service import RouterIntentEvalService
from shared.schemas.query import QueryRequest


def test_router_extracts_domain_doc_type_and_celex():
    router = QueryRouterService()
    route = router.route(
        "Welke verplichtingen uit verordening 32022R2554 gelden nu voor banken?",
        "nl",
    )
    assert route.intent_id == "INT-DORA-COMPLIANCE"
    assert "finance" in route.domains
    assert "regulation" in route.doc_types
    assert route.celex_hint == "32022R2554"
    assert route.time_context == "current"
    assert route.confidence >= 0.9


def test_router_detects_historical_context():
    router = QueryRouterService()
    route = router.route("Wat was historisch de oude versie van CSRD?", "nl")
    assert route.time_context == "historical"
    assert route.intent_id == "INT-HISTORICAL-VERSION"
    assert "sustainability" in route.domains or route.domain_cluster == "financial"


def test_router_employment_intent():
    router = QueryRouterService()
    route = router.route("Welke regels gelden voor uitzendkrachten?", "nl")
    assert route.intent_id == "INT-EMPLOYMENT-AGENCY"
    assert route.domains == ["employment"]
    assert route.celex_hint == "32008L0104"


def test_router_clusters_low_confidence_competition():
    router = QueryRouterService()
    route = router.route("Hoe werkt EU-mededingingsrecht in de praktijk?", "nl")
    assert route.domain_cluster == "financial"
    assert route.confidence >= 0.45


def test_router_intent_eval_fixture_passes():
    report = RouterIntentEvalService().run()
    assert report["passed"], report["failures"]


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
    assert routed.filters.intent_id == "INT-DORA-COMPLIANCE"
    assert routed.filters.router_confidence is not None
    assert routed.filters.domain_cluster == "financial"
