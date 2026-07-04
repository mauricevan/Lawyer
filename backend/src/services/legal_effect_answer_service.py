"""V6 answer framing — explicit effect conclusion and Juridisch effect section."""
import re

from shared.schemas.legal_effect import EffectConclusionHint, LegalEffectAnalysis

_CONCLUSION_LABELS: dict[EffectConclusionHint, str] = {
    "permitted": "Toegestaan",
    "prohibited": "In beginsel niet toegestaan",
    "conditional": "Alleen toegestaan onder voorwaarden",
}

_EFFECT_EXPLANATIONS: dict[str, str] = {
    "discrimination_by_establishment": (
        "De maatregel behandelt marktdeelnemers ongelijk op basis van vestiging of "
        "toelatingscriteria. Onder EU-recht (vrij verkeer en country-of-origin voor "
        "e-diensten) zijn dergelijke beperkingen in beginsel problematisch."
    ),
    "market_access_prohibition": (
        "De maatregel blokkeert of beperkt directe toegang tot de interne markt. "
        "EU-recht staat lidstaten niet toe zomaar markttoegang te weigeren."
    ),
    "additional_requirement": (
        "De lidstaat legt extra nationale voorwaarden op boven het geharmoniseerde EU-kader. "
        "Dat is alleen toegestaan waar EU-recht ruimte laat of een duidelijke uitzondering biedt."
    ),
    "licensing_or_authorisation": (
        "De maatregel vereist voorafgaande toestemming of vergunning. "
        "EU-recht beperkt wanneer lidstaten voorafgaande autorisatie mogen eisen."
    ),
    "procedural_burden": (
        "De maatregel legt administratieve verplichtingen op. "
        "Die moeten evenredig zijn en binnen het EU-kader passen."
    ),
    "enforcement_measure": (
        "De maatregel betreft handhaving of toezicht. "
        "EU-recht bepaalt wanneer en hoe lidstaten mogen handhaven."
    ),
}


def enrich_layperson_answer(answer_text: str, effect: LegalEffectAnalysis) -> str:
    """Insert V6 sections: explicit kort antwoord + Juridisch effect."""
    kort = _kort_antwoord_line(effect)
    effect_section = _juridisch_effect_section(effect)
    if "## Juridisch effect" in answer_text:
        return answer_text
    if "## Kort antwoord" in answer_text:
        return re.sub(
            r"(## Kort antwoord\n)(.*?)(\n\n## )",
            rf"\1{kort}\n\n{effect_section}\n\n\3",
            answer_text,
            count=1,
            flags=re.DOTALL,
        )
    return f"## Kort antwoord\n{kort}\n\n{effect_section}\n\n{answer_text}"


def _kort_antwoord_line(effect: LegalEffectAnalysis) -> str:
    label = _CONCLUSION_LABELS.get(effect.effect_conclusion_hint, "Onder voorwaarden")
    nuance = {
        "high": "De beperking is juridisch zwaarwegend.",
        "medium": "De beperking heeft substantiële juridische gevolgen.",
        "low": "De beperking is beperkt van omvang.",
    }.get(effect.restriction_strength, "")
    return f"**{label}.** {nuance}".strip()


def _juridisch_effect_section(effect: LegalEffectAnalysis) -> str:
    body = _EFFECT_EXPLANATIONS.get(
        effect.legal_effect_type,
        "De nationale maatregel heeft een juridisch effect dat getoetst moet worden aan EU-recht.",
    )
    return f"## Juridisch effect\n{body}"
