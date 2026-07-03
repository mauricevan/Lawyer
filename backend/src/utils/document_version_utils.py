"""Version CELEX helpers (plan13 AD). Owner: backend platform."""
from backend.src.utils.document_version_config import version_resolution_policy

_DEFAULT_PRIORITY = ["consolidated", "base", "amendment", "corrigendum"]


def extract_base_celex(celex: str) -> str:
    """Strip corrigendum suffix to obtain the base act CELEX."""
    marker = "R("
    if marker in celex:
        return celex.split(marker, 1)[0]
    return celex


def version_priority_rank(version_type: str | None) -> int:
    """Higher rank wins during default retrieval conflict resolution."""
    order = version_resolution_policy().get("priority_order", _DEFAULT_PRIORITY)
    normalized = (version_type or "base").lower()
    if normalized in order:
        return len(order) - order.index(normalized)
    return 0


def chunk_version_type(chunk: dict) -> str:
    return str(chunk.get("version_type", "base")).lower()
