"""Shared assertions for declarant-style acceptance tests."""
from __future__ import annotations

from dataclasses import dataclass

_EU_RULES_SECTIONS = ("## wat de eu-regels zeggen", "## uitleg")


def _has_required_section(lowered: str, section: str) -> bool:
    if section in lowered:
        return True
    if section == "## wat de eu-regels zeggen":
        return any(marker in lowered for marker in _EU_RULES_SECTIONS)
    return False


_FORBIDDEN = (
    "marktdeelnemers onder",
    "governance, transparantie, rapportage",
    "celex ,",
    "ik kon geen volledig onderbouwd antwoord",
)


@dataclass(frozen=True)
class DeclarantExpectation:
    """Minimum quality bar for one acceptance scenario."""

    scenario_id: str
    required_celex: frozenset[str] = frozenset()
    forbidden_celex: frozenset[str] = frozenset()
    require_adequate: bool = True
    require_sections: tuple[str, ...] = (
        "## kort antwoord",
        "## wat de eu-regels zeggen",
    )
    require_national_boundary: bool = False
    require_uncertainties: bool = False
    require_article_ref: bool = True
    require_all_celex: bool = False
    required_article_markers: frozenset[str] = frozenset()
    required_text_snippets: frozenset[str] = frozenset()
    require_official_text_section: bool = False
    require_research_verified: bool = False


def forbidden_markers(text: str) -> list[str]:
    lowered = (text or "").lower()
    return [marker for marker in _FORBIDDEN if marker in lowered]


def assert_declarant_answer(
    scenario_id: str,
    answer: str,
    coverage_status: str,
    chunk_celexes: set[str],
    expectation: DeclarantExpectation,
    research_trace: dict | None = None,
) -> list[str]:
    """Return list of failure reasons (empty = pass)."""
    failures: list[str] = []
    lowered = (answer or "").lower()
    failures.extend(f"{scenario_id}: forbidden '{m}'" for m in forbidden_markers(answer))
    if expectation.require_adequate and coverage_status != "adequate":
        failures.append(f"{scenario_id}: expected adequate, got {coverage_status}")
    if coverage_status == "adequate":
        for section in expectation.require_sections:
            if not _has_required_section(lowered, section):
                failures.append(f"{scenario_id}: missing section {section}")
        if expectation.require_article_ref and "artikel" not in lowered and "article" not in lowered:
            failures.append(f"{scenario_id}: no article reference")
        if expectation.required_celex:
            found = expectation.required_celex & chunk_celexes
            missing = expectation.required_celex - chunk_celexes
            if expectation.require_all_celex and missing:
                failures.append(
                    f"{scenario_id}: missing CELEX {sorted(missing)}, got {sorted(chunk_celexes)}"
                )
            elif not found:
                failures.append(
                    f"{scenario_id}: need CELEX {sorted(expectation.required_celex)}, "
                    f"got {sorted(chunk_celexes)}"
                )
        for bad in expectation.forbidden_celex:
            if bad in chunk_celexes and expectation.require_adequate:
                failures.append(f"{scenario_id}: forbidden CELEX {bad} in chunks")
        if expectation.require_national_boundary and "eu-recht en nationaal recht" not in lowered:
            failures.append(f"{scenario_id}: missing EU/national boundary")
        if expectation.require_uncertainties and "onzeker" not in lowered:
            failures.append(f"{scenario_id}: missing uncertainties section")
        for marker in expectation.required_article_markers:
            if marker.lower() not in lowered:
                failures.append(f"{scenario_id}: missing article marker {marker}")
        for snippet in expectation.required_text_snippets:
            if snippet.lower() not in lowered:
                failures.append(f"{scenario_id}: missing text snippet '{snippet}'")
        if expectation.require_official_text_section and "## officiële tekst" not in lowered:
            failures.append(f"{scenario_id}: missing ## Officiële tekst section")
    if expectation.require_research_verified:
        reason = (research_trace or {}).get("terminated_reason")
        if reason != "verified":
            failures.append(f"{scenario_id}: research loop not verified ({reason})")
    return failures
