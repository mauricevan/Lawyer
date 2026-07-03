"""Offline sample text for CI integration eval (plan11 AD)."""
from typing import Any

_CI_TEMPLATE = (
    "{title}. Deze regelgeving bevat verplichtingen voor {keyword}. "
    "Artikel 1 definieert de reikwijdte. Artikel 2 stelt eisen aan naleving."
)

_CI_KEYWORDS: dict[str, str] = {
    "32016R0679": "GDPR en persoonsgegevens",
    "32024R1689": "AI Act en kunstmatige intelligentie",
    "32022R2554": "DORA en digitale operationele veerkracht",
    "32019L1152": "transparante arbeidsvoorwaarden",
    "32003L0088": "arbeidstijden en rusttijden",
    "32008L0104": "uitzendarbeid",
}

_LANG_KEYWORDS: dict[str, dict[str, str]] = {
    "fr": {
        "32016R0679": "RGPD et données personnelles",
        "32024R1689": "AI Act et intelligence artificielle",
        "32022R2554": "DORA et résilience opérationnelle",
    },
    "de": {
        "32016R0679": "DSGVO und personenbezogene Daten",
        "32024R1689": "AI Act und künstliche Intelligenz",
        "32022R2554": "DORA und operative Resilienz",
    },
    "es": {
        "32016R0679": "RGPD y datos personales",
        "32024R1689": "AI Act e inteligencia artificial",
        "32022R2554": "DORA y resiliencia operativa",
    },
}


def _article(celex: str, language: str, title: str) -> list[dict[str, Any]]:
    keyword = _LANG_KEYWORDS.get(language, {}).get(celex) or _CI_KEYWORDS.get(celex, celex)
    text = _CI_TEMPLATE.format(title=title, keyword=keyword)
    return [{"article_number": "1", "subdivision_type": "article", "text": text}]


def build_ci_samples() -> dict[str, list[dict[str, Any]]]:
    samples: dict[str, list[dict[str, Any]]] = {}
    pairs = [
        ("32016R0679", "nl", "GDPR"),
        ("32024R1689", "nl", "AI Act"),
        ("32022R2554", "nl", "DORA"),
        ("32019L1152", "nl", "Transparent Work"),
        ("32003L0088", "nl", "Arbeidstijden"),
        ("32016R0679", "fr", "GDPR"),
        ("32024R1689", "fr", "AI Act"),
        ("32022R2554", "fr", "DORA"),
        ("32016R0679", "de", "GDPR"),
        ("32024R1689", "de", "AI Act"),
        ("32022R2554", "de", "DORA"),
        ("32016R0679", "es", "GDPR"),
        ("32024R1689", "es", "AI Act"),
        ("32022R2554", "es", "DORA"),
    ]
    for celex, language, title in pairs:
        samples[f"{celex}:{language}"] = _article(celex, language, title)
    return samples
