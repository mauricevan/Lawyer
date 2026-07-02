# Plan4 exit-gap — open punten vóór formele sign-off

Plan5 exit-criteria verwijzen naar plan4-afsluiting. Technische werkstromen E/F/G zijn grotendeels af; onderstaande items zijn **organisatorisch** of **deferred**.

| plan4 item | Status | Actie | Target |
|---|---|---|---|
| Verwijderingsverzoeken proces | Open | Documenteer GDPR-verwijderflow in `docs/legal/data-subject-requests.md` | Q3 wk 6 |
| Log-integriteitstrategie | Open | ADR voor append-only audit store of externe SIEM | Q4 2026 |
| 0 kritieke security findings | Open | Sluit resterende pentest P2's of accepteer met mitigatie | Q3 review |
| 100% releasechecks op prod | ⏳ | Eerste tag-release via `release-gate.yml` | Bij v1.0.0 tag |
| Auditrapportages maandelijks | ⏳ | Eerste maandrapport na productie-deploy | Q3/Q4 |
| SLO adherence | ⏳ | Prometheus in prod + 30d window | Na pilot |
| Compliance/security sign-off | Open | Checklist door stakeholder (solo: schriftelijk akkoord in ADR) | Q3 wk 8 |
| Operations governance adopted | ✅ | Runbooks, SLOs, hotfix, escalation actief | — |

## Besluit solo-team

Formele plan4-sign-off = alle P0/P1 technische items groen + bovenstaande documentatie af of expliciet naar Q4 verschoven met entry in [technical-debt-register.md](../ops/technical-debt-register.md).

Koppeling: [plan5-kpi-scorecard.md](./plan5-kpi-scorecard.md) §3 exit-criteria.
