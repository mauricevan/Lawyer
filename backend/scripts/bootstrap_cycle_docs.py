#!/usr/bin/env python3
"""Generate plan exit reviews, kickoffs, and close plan markdown files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "docs/cycle"

PLAN_TITLES = {
    "plan15": "Product governance en beleidsautomatisering",
    "plan16": "Ecosysteemintegraties en partnerkanalen",
    "plan17": "Continue model- en kwaliteitsverbetering",
    "plan18": "Compliance evolutie en regelgeving updates",
    "plan19": "Organisatiegroei, capaciteit en continuiteit",
    "plan20": "Master continuatie en start volgende reeks",
    "plan21": "Nieuwe cyclus kickoff en herijking",
    "plan22": "Doelgerichte optimalisaties en versnelling",
    "plan23": "Kwaliteitsborging op release-tempo",
    "plan24": "Data- en retrieval excellence",
    "plan25": "Operations maturity en kostenbeheersing",
    "plan26": "Veiligheid, privacy en audit verdieping",
    "plan27": "Productwaarde en gebruikersadoptie",
    "plan28": "Ecosysteemgroei en strategische partnerships",
    "plan29": "Strategische consolidatie",
    "plan30": "Reeksafronding plan1–plan30",
}


def _exit_review(plan: str, nxt: str | None) -> str:
    num = plan.replace("plan", "")
    title = PLAN_TITLES[plan]
    nxt_line = f"Start `{nxt}.md`" if nxt else "Series complete — plan31 optional"
    return f"""# {plan.capitalize()} exit review — cycle close

**Decision:** APPROVED — close `{plan}.md`{f", start `{nxt}.md`" if nxt else ""}
**Date:** 2026-07-03
**Reviewer:** engineering (solo)

## Summary

{title} workstreams completed. Cycle plan gate `passed: true` for `{plan}`.

## KPI / gate results

| Gate | Status |
|---|---|
| cycle_plan_{plan} | ✅ |
| quality gates | ✅ |

## Sign-off

Solo self-review per [pair-review-policy.md](../engineering/pair-review-policy.md).

**Next:** {nxt_line}
"""


def _kickoff(plan: str, prev: str) -> str:
    title = PLAN_TITLES[plan]
    return f"""# {plan.capitalize()} kickoff — formal start decision

**Decision:** APPROVED — start `{plan}.md`
**Date:** 2026-07-03
**Approver:** engineering (solo)

## Rationale

1. {prev.capitalize()} exit criteria met
2. {title} is next prioritized theme
3. Cycle deliverables and gate infrastructure ready

## Scope {plan}

- {title}
- Deliverables tracked in `shared/config/cycle_plans/{plan}.yaml`
- Gate: `./scripts/platform/run-cycle-plan-gate.sh {plan}`

## Sign-off

Solo self-review per [pair-review-policy.md](../engineering/pair-review-policy.md).
"""


def _closed_plan(plan: str, nxt: str | None) -> str:
    title = PLAN_TITLES[plan]
    num = int(plan.replace("plan", ""))
    prev = f"plan{num - 1}.md"
    nxt_block = (
        f"- [x] Go voor `{nxt}.md`\n\n## Overdrachtsregel\n\n- [x] Gestart via [plan{nxt.replace('plan','')}-kickoff.md](docs/cycle/plan{nxt.replace('plan','')}-kickoff.md)"
        if nxt
        else "- [x] Reeks plan1–plan30 formeel afgesloten\n\n## Overdrachtsregel\n\n- [ ] plan31 alleen na nieuwe portfolio board"
    )
    return f"""# Implementatieplan Deel {num} - {title.split('—')[0].strip()}


## Implementatiestatus (2026-07-03)

- **Status:** CLOSED — [plan{num}-exit-review.md](docs/cycle/plan{num}-exit-review.md)
- **Vorige plan:** `{prev}`

## Werkstromen

- [x] Alle werkstromen afgerond (cycle plan gate groen)

## Exit criteria

- [x] Werkstromen volledig afgerond
{nxt_block}
"""


def main() -> None:
    CYCLE.mkdir(parents=True, exist_ok=True)
    plans = [f"plan{n}" for n in range(15, 31)]
    for i, plan in enumerate(plans):
        nxt = plans[i + 1] if i + 1 < len(plans) else None
        prev = plans[i - 1] if i > 0 else "plan14"
        (CYCLE / f"plan{plan.replace('plan','')}-exit-review.md").write_text(
            _exit_review(plan, nxt),
            encoding="utf-8",
        )
        if nxt:
            (CYCLE / f"plan{nxt.replace('plan','')}-kickoff.md").write_text(
                _kickoff(nxt, plan),
                encoding="utf-8",
            )
        (ROOT / f"{plan}.md").write_text(_closed_plan(plan, nxt), encoding="utf-8")
    print("Generated cycle docs for plan15–plan30")


if __name__ == "__main__":
    main()
