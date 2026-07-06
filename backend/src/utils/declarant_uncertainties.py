"""Topic-specific uncertainty bullets for declarant-style layperson answers."""


def render_uncertainties_section(question: str) -> str | None:
    """Return markdown uncertainties block when the question needs explicit caveats."""
    lowered = (question or "").lower()
    bullets = (
        _customs_bullets(lowered)
        or _privacy_bullets(lowered)
        or _product_safety_bullets(lowered)
        or _identity_bullets(lowered)
    )
    if not bullets:
        return None
    lines = ["## Onzekerheden", ""]
    lines.extend(f"- {item}" for item in bullets)
    return "\n".join(lines)


def _customs_bullets(lowered: str) -> list[str] | None:
    if not any(word in lowered for word in ("douane", "invoer", "import", "china", "pakket", "etsy")):
        return None
    return [
        "**Bent u importeur of verkoopt u als platform/marktplaats?** De plichten verschillen.",
        "**Productcategorie** (voedsel, elektronica, cosmetica) kan extra regels geven.",
        "**IOSS/one-stop-shop** of andere vereenvoudigde regeling kan van toepassing zijn — hangt af van uw rol en zending.",
        "**Waarde en herkomst** van de zending bepalen of vrijstellingen gelden.",
    ]


def _identity_bullets(lowered: str) -> list[str] | None:
    if not any(word in lowered for word in ("legitim", "identif", "paspoort", "eidas", "identiteitskaart")):
        return None
    return [
        "**Welk land** (alleen NL of reizen in de EU)?",
        "**Alleen online** of ook fysiek loket?",
        "**EU-burger** of derdelander?",
    ]


def _privacy_bullets(lowered: str) -> list[str] | None:
    if not any(word in lowered for word in ("avg", "gdpr", "privacy", "e-mail", "email", "persoonsgegeven", "gegevens")):
        return None
    if any(word in lowered for word in ("douane", "invoer", "import")):
        return None
    return [
        "**Arbeidscontext:** nationale wet en cao kunnen extra bescherming geven naast de AVG.",
        "**Rechtsgrond:** hangt af van of u toestemming gaf en voor welk doel gegevens zijn verzameld.",
        "**Doelwijziging:** doorgeven voor reclame is vaak een nieuw doel — niet automatisch toegestaan.",
    ]


def _product_safety_bullets(lowered: str) -> list[str] | None:
    if not any(word in lowered for word in ("terugroep", "speelgoed", "onveilig", "productveilig", "gpsr")):
        return None
    return [
        "**Uw rol:** fabrikant, importeur of verkoper bepaalt welke plichten op u rusten.",
        "**Speelgoed:** extra EU-speelgoedregels kunnen naast de GPSR gelden.",
        "**Ernst van het risico:** bepaalt of melding aan de autoriteit direct nodig is.",
    ]
