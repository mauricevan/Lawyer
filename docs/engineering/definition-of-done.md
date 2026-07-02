# Definition of Done (plan8 R)

Gedeeld voor backend, frontend, ingestion en platform. Geen merge naar `main` zonder deze checklist.

## Code

- [ ] Wijziging past in bestaande architectuur (routes → services → data)
- [ ] Bestanden ≤ 250 regels; functies ≤ 20 regels waar mogelijk
- [ ] Geen secrets, geen PII in logs
- [ ] Input validatie op alle nieuwe/gewijzigde externe grenzen

## Tests

- [ ] Unit tests voor nieuwe service-/utility-logica
- [ ] Edge case: lege input, null, ongeldige types
- [ ] `pytest backend/tests -m "not integration" -q` groen
- [ ] Frontend: `npm test -- --run` groen bij UI-wijzigingen

## Security & compliance

- [ ] Auth/RBAC op nieuwe endpoints (tenzij gedocumenteerde uitzondering)
- [ ] Kritieke paden: [pair-review-policy.md](./pair-review-policy.md)
- [ ] SSRF/injection checks waar externe URLs of SQL betrokken

## Release & docs

- [ ] `.env.example` bijgewerkt bij nieuwe config
- [ ] Relevante runbook/ADR bij structurele beslissingen
- [ ] Conventional Commit message
- [ ] Plan-doc checkbox bij plan-gebonden werk

## Release naar productie

- [ ] `./scripts/ops/run-release-checklist.sh` groen
- [ ] Bij retrieval/prompt-wijziging: `./scripts/qa/run-release-eval-suite.sh`
- [ ] `./scripts/ops/run-quality-gate-audit.sh` groen

## Solo-team

Geen tweede reviewer: self-review + `PAIR_REVIEW_ACK=yes ./scripts/ops/check-pair-review.sh` na 30 min pauze.

Zie ook: [release-standards.md](./release-standards.md), [AGENTS.md](../../AGENTS.md)
