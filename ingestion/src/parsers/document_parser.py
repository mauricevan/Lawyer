"""Document parser facade — Formex first, XHTML fallback."""
from typing import Any

from ingestion.src.parsers.formex_parser import FormexParser
from ingestion.src.parsers.xhtml_parser import XhtmlParser


class DocumentParser:
    """Parses raw document bytes into subdivisions."""

    def __init__(self) -> None:
        self._formex = FormexParser()
        self._xhtml = XhtmlParser()

    def parse(self, content: bytes, celex: str, content_type: str = "html") -> list[dict[str, Any]]:
        if content_type in ("xml", "formex") or content[:5] == b"<?xml":
            try:
                return self._formex.parse(content, celex)
            except Exception:
                pass
        return self._xhtml.parse(content, celex)
