"""Build LLM synthesis context from chunks and/or planner templates."""
from typing import Any

from backend.src.services.legal_planner_template_loader import resolve_obligation_templates
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.regulation_label_service import regulation_label
from backend.src.utils.legal_chunk_text import clean_chunk_text
from backend.src.utils.legal_planner_prompt_context import build_planner_interpretation_hints
from backend.src.utils.legal_question_interpretation import infer_legal_context

_MAX_CONTEXT_CHARS = 6000


def build_synthesis_context(question: str, chunks: list[dict[str, Any]]) -> str:
    """Prefer NL chunk text; fall back to planner obligation templates."""
    chunk_ctx = _context_from_chunks(chunks)
    if chunk_ctx:
        return chunk_ctx
    return _context_from_planner_templates(question)


def build_synthesis_hints(question: str) -> str:
    """Interpretation hints for synthesis prompt."""
    return build_planner_interpretation_hints(question)


def _context_from_chunks(chunks: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    total = 0
    for chunk in chunks[:8]:
        text = clean_chunk_text(str(chunk.get("text", "")))
        if len(text) < 80:
            continue
        celex = chunk.get("celex", "")
        article = chunk.get("article_number", "")
        label = regulation_label(str(celex)) if celex else "EU-regelgeving"
        block = f"[{label}, artikel {article}]\n{text[:900]}"
        if total + len(block) > _MAX_CONTEXT_CHARS:
            break
        blocks.append(block)
        total += len(block)
    return "\n\n---\n\n".join(blocks)


def _context_from_planner_templates(question: str) -> str:
    plan = LegalSourcePlannerService().plan(question)
    if not plan:
        return ""
    templates = resolve_obligation_templates(plan.plan_id, plan.celex, plan.legal_domain)
    if not templates:
        return ""
    actor, issue = infer_legal_context(question)
    reg_label = regulation_label(plan.celex)
    lines = [
        f"Instrument: {reg_label} ({plan.celex})",
        f"legal_actor: {actor}; legal_issue: {issue}",
        "Samenvatting verplichtingen uit planner:",
    ]
    for template in templates[:6]:
        lines.append(
            f"- Art. {template.get('article', '?')} {template.get('label', '')}: "
            f"{template.get('uitleg', '')}"
        )
    return "\n".join(lines)
