"""Map legacy markdown answers to/from semantic explanation sections."""
import re
import uuid

from shared.schemas.legal_explanation import ExplanationSectionKey, ExplanationSections

_HEADING_TO_KEY: tuple[tuple[str, ExplanationSectionKey], ...] = (
    (r"kort antwoord", ExplanationSectionKey.short_answer),
    (r"short answer", ExplanationSectionKey.short_answer),
    (r"wat de eu-regels zeggen", ExplanationSectionKey.law_says),
    (r"juridische basis", ExplanationSectionKey.law_says),
    (r"wettelijke grondslag", ExplanationSectionKey.law_says),
    (r"juridische grondslag", ExplanationSectionKey.law_says),
    (r"wat betekent dit", ExplanationSectionKey.practical_meaning),
    (r"wat dit in de praktijk", ExplanationSectionKey.practical_meaning),
    (r"praktische uitleg", ExplanationSectionKey.practical_meaning),
    (r"juridische bronnen", ExplanationSectionKey.legal_sources),
    (r"^bronnen$", ExplanationSectionKey.legal_sources),
    (r"offici[eë]le tekst", ExplanationSectionKey.legal_sources),
    (r"onzekerheden", ExplanationSectionKey.uncertainties),
    (r"wat u wél kunt doen", ExplanationSectionKey.uncertainties),
    (r"let op", ExplanationSectionKey.disclaimer),
    (r"disclaimer", ExplanationSectionKey.disclaimer),
)

_RENDER_HEADINGS_NL: dict[ExplanationSectionKey, str] = {
    ExplanationSectionKey.short_answer: "Kort antwoord",
    ExplanationSectionKey.law_says: "Wat de EU-regels zeggen",
    ExplanationSectionKey.practical_meaning: "Wat dit in de praktijk betekent",
    ExplanationSectionKey.legal_sources: "Juridische bronnen",
    ExplanationSectionKey.uncertainties: "Onzekerheden",
    ExplanationSectionKey.disclaimer: "Disclaimer",
}


def retrieval_context_id(chunks: list[dict]) -> str:
    """Stable id for immutable retrieval snapshot reference."""
    if not chunks:
        return str(uuid.uuid4())
    parts = sorted(f"{c.get('celex', '')}:{c.get('chunk_id', '')}" for c in chunks)
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "|".join(parts[:20])))


def markdown_to_sections(text: str, fallback_disclaimer: str = "") -> ExplanationSections:
    """Parse ## headings into semantic sections; unmapped body → practical_meaning."""
    sections = {key.value: "" for key in ExplanationSectionKey}
    if not text.strip():
        return _empty_sections(fallback_disclaimer)
    parts = re.split(r"\n(?=## )", text.strip())
    for part in parts:
        if not part.startswith("## "):
            sections[ExplanationSectionKey.short_answer.value] = part.strip()
            continue
        lines = part.split("\n", 1)
        heading = lines[0].lstrip("#").strip().lower()
        body = lines[1].strip() if len(lines) > 1 else ""
        key = _match_heading(heading)
        if key:
            sections[key.value] = _append_section(sections[key.value], body)
        else:
            block = f"## {lines[0].lstrip('#').strip()}\n{body}" if body else f"## {heading}"
            sections[ExplanationSectionKey.practical_meaning.value] = _append_section(
                sections[ExplanationSectionKey.practical_meaning.value], block,
            )
    return _finalize_sections(sections, fallback_disclaimer)


def sections_to_markdown(sections: ExplanationSections) -> str:
    """Render semantic sections to user markdown (dumb template)."""
    blocks: list[str] = []
    for key in ExplanationSectionKey:
        body = getattr(sections, key.value, "").strip()
        if not body:
            continue
        blocks.append(f"## {_RENDER_HEADINGS_NL[key]}\n{body}")
    return "\n\n".join(blocks)


def _match_heading(heading: str) -> ExplanationSectionKey | None:
    for pattern, key in _HEADING_TO_KEY:
        if re.search(pattern, heading):
            return key
    return None


def _append_section(existing: str, body: str) -> str:
    if not existing:
        return body
    return f"{existing}\n\n{body}"


def _empty_sections(disclaimer: str) -> ExplanationSections:
    return ExplanationSections(
        short_answer="",
        law_says="",
        practical_meaning="",
        legal_sources="",
        uncertainties="",
        disclaimer=disclaimer,
    )


def _finalize_sections(raw: dict[str, str], disclaimer: str) -> ExplanationSections:
    if not raw.get("disclaimer") and disclaimer:
        raw["disclaimer"] = disclaimer
    if not raw.get("short_answer") and raw.get("practical_meaning"):
        raw["short_answer"] = raw["practical_meaning"][:280]
    return ExplanationSections(
        short_answer=raw.get("short_answer", ""),
        law_says=raw.get("law_says", ""),
        practical_meaning=raw.get("practical_meaning", ""),
        legal_sources=raw.get("legal_sources", ""),
        uncertainties=raw.get("uncertainties", ""),
        disclaimer=raw.get("disclaimer", disclaimer),
    )
