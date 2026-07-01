"""Formats legal citations for clipboard, Word, and BibTeX."""
from shared.schemas.citation import Citation


class CitationFormatter:
    """Produces copy-paste ready legal citation strings."""

    def to_legal_format(self, citation: Citation) -> str:
        parts = []
        if citation.article:
            parts.append(f"Artikel {citation.article}")
        reg_title = citation.title or self._celex_to_title(citation.celex)
        parts.append(reg_title)
        if citation.trust.oj_reference:
            parts.append(f"PbEU {citation.trust.oj_reference}")
        return ", ".join(parts)

    def to_clipboard(self, citation: Citation) -> str:
        legal = self.to_legal_format(citation)
        url = citation.eurlex_url
        return f"{legal}\n{citation.excerpt[:300]}\nBron: {url}"

    def to_bibtex(self, citation: Citation) -> str:
        key = citation.celex.replace("(", "").replace(")", "")
        title = citation.title or citation.celex
        return (
            f"@misc{{{key},\n"
            f"  title = {{{title}}},\n"
            f"  howpublished = {{EUR-Lex}},\n"
            f"  url = {{{citation.eurlex_url}}},\n"
            f"  note = {{CELEX {citation.celex}}}\n"
            f"}}"
        )

    def _celex_to_title(self, celex: str) -> str:
        year = celex[1:5] if len(celex) > 5 else ""
        return f"Verordening (EU) {year}/{celex[5:9]}" if "R" in celex else f"CELEX {celex}"
