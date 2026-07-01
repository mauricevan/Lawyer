"""Formex XML parser for structured EU legal documents."""
import re
from typing import Any
from xml.etree import ElementTree as ET


class FormexParser:
    """Parses Formex XML into article-level subdivisions."""

    def parse(self, xml_bytes: bytes, celex: str) -> list[dict[str, Any]]:
        root = ET.fromstring(xml_bytes)
        title = self._find_title(root)
        articles = self._find_articles(root)
        if not articles:
            articles = [{"article_number": None, "subdivision_type": "body", "text": self._all_text(root)}]
        return [{"title": title, "celex": celex, **a} for a in articles if a.get("text")]

    def _find_title(self, root: ET.Element) -> str:
        for tag in ["TITLE", "TI", "SHORT-TITLE"]:
            for el in root.iter(tag):
                text = self._element_text(el)
                if text:
                    return text[:500]
        return "Untitled"

    def _find_articles(self, root: ET.Element) -> list[dict[str, Any]]:
        results = []
        for el in root.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag in ("ARTICLE", "ART", "PREAMBLE", "RECITAL"):
                text = self._element_text(el)
                if len(text) < 20:
                    continue
                num = el.get("NUM") or el.get("NUMBER") or self._extract_num(text)
                sub_type = "recital" if tag == "RECITAL" else "article"
                results.append({
                    "article_number": num,
                    "subdivision_type": sub_type,
                    "text": text,
                })
        return results

    def _extract_num(self, text: str) -> str | None:
        match = re.search(r"(?:Article|Artikel)\s+(\d+)", text[:80], re.I)
        return match.group(1) if match else None

    def _element_text(self, el: ET.Element) -> str:
        return " ".join(el.itertext()).strip()

    def _all_text(self, root: ET.Element) -> str:
        return self._element_text(root)[:50000]
