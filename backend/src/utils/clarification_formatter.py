"""V10.3 ILCL answer formatter."""
from backend.src.utils.clarification_chip_filter import filter_layperson_chips
from backend.src.utils.layperson_clarification_copy import (
    detect_topic_label,
    format_layperson_clarification_intro,
)
from shared.schemas.legal_clarification import LegalClarificationResult


def format_clarification_section(
    result: LegalClarificationResult,
    audience: str = "layperson",
) -> str:
    """Render ILCL output for the user-facing answer."""
    if result.mode == "skip":
        return ""
    if result.mode == "assumption":
        return _format_assumption(result, audience)
    if result.mode == "questions":
        return _format_questions(result, audience)
    if result.mode == "scenarios":
        return _format_scenarios(result, audience)
    return ""


def clarification_prompt_from_result(result: LegalClarificationResult) -> str | None:
    """Primary follow-up prompt shown in the UI."""
    if result.mode == "questions" and result.questions:
        return result.questions[0].prompt
    if result.mode == "scenarios":
        return "Welke situatie beschrijft het best wat u bedoelt?"
    return None


def _format_assumption(result: LegalClarificationResult, audience: str) -> str:
    if audience == "layperson":
        return (
            f"{result.assumption_text}\n\n"
            "_Ik ga verder met deze aanname en zoek daarna de relevante EU-regels voor u op._"
        )
    return (
        "## Juridische verduidelijking\n\n"
        f"{result.assumption_text}\n\n"
        "_Ik ga verder met deze aanname en haal daarna pas EUR-Lex-bronnen op._"
    )


def _format_questions(result: LegalClarificationResult, audience: str) -> str:
    if audience == "layperson" and result.questions:
        question = result.enriched_question or ""
        prompt = result.questions[0].prompt
        topic = detect_topic_label(question)
        return format_layperson_clarification_intro(question, prompt, topic)
    lines = ["## Juridische verduidelijking\n"]
    lines.append(
        "Ik kan dit juridisch pas precies beoordelen als ik meer weet.\n"
        "**Kunt u dit verduidelijken?**\n"
    )
    for index, item in enumerate(result.questions, start=1):
        lines.append(f"{index}. {item.prompt}")
        if item.options:
            lines.append("   - " + "\n   - ".join(item.options))
    lines.append(
        "\n💡 Daarna kan ik exact zeggen welke EU-regels gelden "
        "(DSA / e-commerce / consumentenrecht / etc.)."
    )
    return "\n".join(lines)


def _format_scenarios(result: LegalClarificationResult, audience: str) -> str:
    if audience == "layperson":
        question = result.enriched_question or ""
        topic = detect_topic_label(question)
        intro = format_layperson_clarification_intro(
            question,
            "Uw vraag kan op een paar manieren worden begrepen — welke past het best?",
            topic,
        )
        return intro
    lines = ["## Juridische verduidelijking\n"]
    lines.append("Op basis van uw vraag zie ik meerdere mogelijke interpretaties:\n")
    for scenario in result.scenarios:
        frameworks = ", ".join(scenario.frameworks)
        lines.append(f"**{scenario.id}. {scenario.label}**")
        lines.append(f"→ {scenario.description}")
        lines.append(f"→ {frameworks}\n")
    lines.append("Welke bedoelt u?")
    return "\n".join(lines)


def verification_questions_from_result(
    result: LegalClarificationResult,
    audience: str = "layperson",
) -> list[str]:
    """Flatten ILCL options into clickable follow-up actions."""
    if result.mode == "questions":
        options: list[str] = []
        for question in result.questions:
            if question.options:
                options.extend(question.options)
            elif audience != "layperson":
                options.append(question.prompt)
        if audience == "layperson":
            return filter_layperson_chips(options)
        return options[:5]
    if result.mode == "scenarios":
        return [f"{s.id}. {s.label}" for s in result.scenarios]
    return []
