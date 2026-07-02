"""Audit log completeness validation for plan4 F2."""
from backend.src.models.tables import AuditLog

REQUIRED_ROUTE_KEYS = ("retrieval_route",)


def is_audit_entry_complete(entry: AuditLog) -> bool:
    """Return True when mandatory audit fields are populated."""
    if not entry.request_id or not entry.question:
        return False
    if not entry.model:
        return False
    if entry.route is None:
        return False
    route = entry.route if isinstance(entry.route, dict) else {}
    return all(route.get(key) for key in REQUIRED_ROUTE_KEYS)


def summarize_completeness(entries: list[AuditLog]) -> dict[str, float | int]:
    """Compute completeness metrics for a batch of audit rows."""
    total = len(entries)
    if total == 0:
        return {"count": 0, "complete": 0, "incomplete": 0, "completeness_ratio": 1.0}
    complete = sum(1 for entry in entries if is_audit_entry_complete(entry))
    incomplete = total - complete
    return {
        "count": total,
        "complete": complete,
        "incomplete": incomplete,
        "completeness_ratio": round(complete / total, 4),
    }
