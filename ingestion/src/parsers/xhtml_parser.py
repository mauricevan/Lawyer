"""XHTML parser for EUR-Lex document HTML."""
import re
from typing import Any

from bs4 import BeautifulSoup


class XhtmlParser:
    """Extracts structured subdivisions from EUR-Lex HTML."""

    def parse(self, html: bytes, celex: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        title = self._extract_title(soup)
        subdivisions = self._extract_subdivisions(soup)
        if not subdivisions:
            subdivisions = self._fallback_paragraphs(soup)
        return [{"title": title, "celex": celex, **sub} for sub in subdivisions]

    def _extract_title(self, soup: BeautifulSoup) -> str:
        for selector in ["h1", ".eli-title", "title"]:
            el = soup.select_one(selector)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)[:500]
        return "Untitled"

    def _extract_subdivisions(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        results = []
        for div in soup.select("div.eli-subdivision, article, div[id*='art']"):
            text = div.get_text(separator=" ", strip=True)
            if len(text) < 20:
                continue
            article = self._find_article_number(div, text)
            sub_type = "article" if article else "section"
            results.append({
                "article_number": article,
                "subdivision_type": sub_type,
                "text": text,
            })
        return results

    def _find_article_number(self, div: Any, text: str) -> str | None:
        div_id = div.get("id", "")
        match = re.search(r"art[_-]?(\d+)", div_id, re.I)
        if match:
            return match.group(1)
        match = re.search(r"Artikel\s+(\d+)", text[:100], re.I)
        return match.group(1) if match else None

    def _fallback_paragraphs(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        body = soup.find("body") or soup
        text = body.get_text(separator="\n", strip=True)
        chunks = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 100]
        return [
            {"article_number": None, "subdivision_type": "paragraph", "text": c}
            for c in chunks[:200]
        ]
