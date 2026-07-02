# Change approval matrix

| Change type | Voorbeelden | Vereiste reviewers | CI gates |
|---|---|---|---|
| **Standard** | UI copy, docs, tests | 1 engineer | Unit + security-scan |
| **Feature** | Nieuwe API, RAG-wijziging | 1 engineer + product owner | Unit + security + eval (weekly) |
| **Schema** | Alembic migratie | 1 engineer + DBA/on-call | Unit + migratie op staging |
| **Security** | Auth, RBAC, secrets | 1 engineer + security owner | security-scan + pentest checklist |
| **Hotfix** | Productie-incident fix | On-call engineer (post-factum review binnen 24u) | Minimaal gerichte tests + smoke |

## Regels

1. Geen directe commits op `main` — altijd feature branch + PR.
2. Schema-wijzigingen: backwards-compatible voor minimaal één release (nullable columns eerst).
3. Hotfix: merge binnen 2 uur toegestaan; volledige review binnen 24 uur.
4. Breaking API-wijziging: versie-bump `/api/v2` vereist.
