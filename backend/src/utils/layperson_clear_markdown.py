"""Render LaypersonClearAnswer to canonical markdown sections."""
from shared.schemas.layperson_clear_answer import LaypersonClearAnswer

_DEFAULT_LET_OP = (
    "Dit is geen persoonlijk juridisch advies. Raadpleeg een jurist of bevoegde "
    "instantie voor uw specifieke situatie."
)


def render_clear_answer(answer: LaypersonClearAnswer) -> str:
    """Return markdown with fixed section order for layperson audience."""
    sections = [f"## Kort antwoord\n{answer.kort_antwoord.strip()}"]
    if answer.obligations:
        sections.append(_render_obligations_table(answer))
    if answer.voorbeeld.strip():
        sections.append(f"## Voorbeeld\n{answer.voorbeeld.strip()}")
    if answer.juridische_basis:
        sections.append(_render_legal_basis(answer))
    if answer.official_excerpts:
        sections.append(_render_official_text(answer))
    if answer.begrippen:
        sections.append(_render_terms(answer))
    let_op = answer.let_op.strip() or _DEFAULT_LET_OP
    sections.append(f"## Let op\n{let_op}")
    return "\n\n".join(sections)


def _render_obligations_table(answer: LaypersonClearAnswer) -> str:
    rows = ["| Verplichting | Uitleg |", "| --- | --- |"]
    for row in answer.obligations:
        label = row.label.replace("|", "\\|")
        uitleg = row.uitleg.replace("|", "\\|")
        rows.append(f"| {label} | {uitleg} |")
    return "## Wat betekent dit in de praktijk?\n\n" + "\n".join(rows)


def _render_legal_basis(answer: LaypersonClearAnswer) -> str:
    lines = ["## Juridische basis"]
    for item in answer.juridische_basis:
        title = f" – {item.title}" if item.title else ""
        lines.append(f"- **Artikel {item.article}{title}:** {item.uitleg_nl}")
    return "\n".join(lines)


def _render_official_text(answer: LaypersonClearAnswer) -> str:
    parts = [
        "## Officiële tekst",
        "<details>",
        "<summary>Toon letterlijke tekst uit EUR-Lex (ter controle)</summary>",
        "",
    ]
    for excerpt in answer.official_excerpts[:3]:
        heading = excerpt.label or (f"Artikel {excerpt.article}" if excerpt.article else "Bron")
        parts.append(f"**{heading}**")
        parts.append("")
        parts.append(excerpt.text.strip())
        parts.append("")
    parts.append("</details>")
    return "\n".join(parts)


def _render_terms(answer: LaypersonClearAnswer) -> str:
    lines = ["## Begrippen"]
    for term in answer.begrippen:
        lines.append(f"- **{term.term}:** {term.definition_nl}")
    return "\n".join(lines)
