# Pair review policy (plan5 J2)

Wijzigingen aan **kritieke componenten** vereisen een tweede paar ogen vóór merge naar `main`.

## Scope

Gedefinieerd in [critical-components.yaml](./critical-components.yaml):

- RAG pipeline (retrieval, router, cache, live fallback)
- Answer policy & citations
- Auth & SSRF
- Query API + shared schemas
- Admin & audit

## Proces

### Team ≥ 2 engineers

1. Auteur opent PR
2. Reviewer doorloopt [checklist](#review-checklist)
3. Approve vóór merge

### Solo engineer

1. Wacht minimaal 30 min na eigen implementatie (fresh eyes)
2. Doorloop checklist schriftelijk (PR beschrijving of commit body)
3. Draai:

```bash
PAIR_REVIEW_ACK=yes ./scripts/ops/check-pair-review.sh
```

4. Merge pas na groene tests + checklist afgevinkt

## Review checklist

- [ ] Geen secrets, geen PII in logs
- [ ] Input validatie op alle nieuwe/gewijzigde endpoints
- [ ] Auth/RBAC gehandhaafd
- [ ] Tests voor happy path + minstens één edge case
- [ ] Geen bestand >250 regels zonder split-plan
- [ ] SSRF guard op externe URLs
- [ ] Disclaimers/citations policy intact
- [ ] Migratie reversibel indien schema-wijziging

## Automatische gate

```bash
./scripts/ops/check-pair-review.sh              # vs HEAD~1
./scripts/ops/check-pair-review.sh --staged     # pre-commit
PAIR_REVIEW_ACK=yes ./scripts/ops/check-pair-review.sh  # na review
```

Script faalt als kritieke paden wijzigen zonder `PAIR_REVIEW_ACK=yes`.

## Uitzonderingen

- Alleen comment/doc wijzigingen in kritieke paden: geen ACK nodig
- Hotfix P0: ACK post-factum binnen 24u ([hotfix-runbook.md](../ops/hotfix-runbook.md))

## Koppeling CI

Release gate en [run-release-checklist.sh](../../scripts/ops/run-release-checklist.sh) roepen pair-review check aan bij tag builds.
