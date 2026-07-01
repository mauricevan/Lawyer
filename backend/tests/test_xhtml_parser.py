"""Integration tests for XHTML parser with GDPR fixture."""
from ingestion.src.parsers.xhtml_parser import XhtmlParser


GDPR_HTML = b"""
<html><body>
<h1>Verordening GDPR</h1>
<div class="eli-subdivision" id="art_6">
  <p>Artikel 6 Rechtmatigheid van de verwerking.</p>
</div>
<div class="eli-subdivision" id="art_9">
  <p>Artikel 9 Bijzondere categorieen van persoonsgegevens.</p>
</div>
</body></html>
"""


def test_xhtml_parser_extracts_articles() -> None:
    parser = XhtmlParser()
    result = parser.parse(GDPR_HTML, "32016R0679")
    assert len(result) >= 2
    articles = [r.get("article_number") for r in result]
    assert "6" in articles or any("6" in str(a) for a in articles)
