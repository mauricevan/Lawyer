"""Data classification map for plan4 F1 governance."""
from enum import Enum


class DataClass(str, Enum):
    PII = "pii"
    PSEUDO_PII = "pseudo_pii"
    NON_PII = "non_pii"


TABLE_CLASSIFICATION: dict[str, DataClass] = {
    "users": DataClass.PII,
    "conversations": DataClass.PSEUDO_PII,
    "messages": DataClass.PSEUDO_PII,
    "query_logs": DataClass.PSEUDO_PII,
    "query_feedback": DataClass.PSEUDO_PII,
    "audit_logs": DataClass.PSEUDO_PII,
    "live_cache": DataClass.NON_PII,
    "documents": DataClass.NON_PII,
    "chunks": DataClass.NON_PII,
}


def classification_report() -> dict[str, str]:
    """Return table -> classification labels for governance review."""
    return {table: level.value for table, level in TABLE_CLASSIFICATION.items()}
