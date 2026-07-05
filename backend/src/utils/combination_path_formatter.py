"""Format dual-branch combination-path answers for layperson output."""
from __future__ import annotations

from backend.src.services.combination_path_detector_service import branch_display_label


def format_combination_answer(parts: list[dict]) -> str:
    """Render separate sections per branch — never silently merge."""
    intro = (
        "**U stelde meerdere juridische vragen — hieronder per onderdeel:**\n"
    )
    sections: list[str] = [intro]
    for idx, part in enumerate(parts, start=1):
        branch = part.get("branch", "")
        title = part.get("branch_label") or branch_display_label(branch)
        body = (part.get("answer_text") or "").strip()
        if not body:
            body = _gap_fallback(part)
        sections.append(f"### {idx}. {title}\n\n{body}")
    return "\n\n".join(sections)


def _gap_fallback(part: dict) -> str:
    status = part.get("coverage_status") or "insufficient"
    if status == "insufficient":
        return (
            "Voor dit onderdeel heb ik onvoldoende betrouwbare EU-bronnen "
            "om een antwoord te geven."
        )
    return "Voor dit onderdeel kon geen antwoord worden samengesteld."
