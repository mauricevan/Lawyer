"""Audit helper for API input validation coverage."""
from backend.src.security.input_validation_registry import ENDPOINT_VALIDATIONS


def build_coverage_report() -> dict:
    """Return validation coverage summary for CI and docs."""
    total = len(ENDPOINT_VALIDATIONS)
    validated = sum(1 for entry in ENDPOINT_VALIDATIONS if entry.status == "validated")
    gaps = [entry for entry in ENDPOINT_VALIDATIONS if entry.status != "validated"]
    return {
        "total_endpoints": total,
        "validated_endpoints": validated,
        "coverage_percent": round((validated / total) * 100, 2) if total else 100.0,
        "gaps": [
            {"method": gap.method, "path": gap.path, "status": gap.status}
            for gap in gaps
        ],
    }


def run_audit(min_coverage: float = 100.0) -> dict:
    """Fail when validation coverage drops below threshold."""
    report = build_coverage_report()
    if report["coverage_percent"] < min_coverage:
        raise SystemExit(
            f"Input validation audit failed: {report['coverage_percent']}% "
            f"(required {min_coverage}%)"
        )
    return report
