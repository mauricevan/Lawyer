# Incident learnings → coding standards (plan5 J2)

Geconsolideerde lessen uit productie-achtige incidenten, eval-failures en security-oefeningen.  
**Terugkoppeling:** regels hieronder zijn opgenomen in [AGENTS.md](../../AGENTS.md) §13.1.

## Learnings

| ID | Incident / patroon | Les | Code-standaard |
|---|---|---|---|
| IL-001 | EUR-Lex 202/lege HTML | Nooit vertrouwen op live body zonder usable-content check | `CellarRestClient._is_usable_content` |
| IL-002 | Lage retrieval score → hallucinatie | Confidence + verificatievragen bij onzekerheid | `AnswerQualityService` |
| IL-003 | Antwoord zonder bron | Brondenplicht altijd afdwingen | `AnswerPolicyService.enforce_citations` |
| IL-004 | Secret in `.env.example` commit | Placeholders only; scan in pre-commit | `check-secrets.sh` |
| IL-005 | SSRF via user-supplied URL | Allowlist publicaties.europa.eu / eur-lex | `ssrf_guard.py` |
| IL-006 | Prompt injection | Block vóór LLM-call | `GuardrailsService` |
| IL-007 | Postgres poort conflict lokaal | Documenteer `docker-compose.local.yml` | onboarding + troubleshooting |
| IL-008 | JWT uit in dev per ongeluk prod | Staging/prod: `JWT_AUTH_REQUIRED=true` | TD-003 debt register |
| IL-009 | Eval niet gedraaid vóór release | Release checklist verplicht | `run-release-checklist.sh` |
| IL-010 | Alert zonder runbook | Elke alert linkt naar runbook | `alert-fatigue-review.md` |

## Post-mortem template

```markdown
## Incident IL-0XX — titel — datum

**Impact:** ...
**Root cause:** ...
**Detection:** ...
**Fix:** ...
**Prevention:** (test / guard / runbook update)
**AGENTS.md update needed:** ja/nee
```

## Maandelijkse terugkoppeling

1. Nieuwe learning → rij in tabel + eventueel AGENTS.md §13.1
2. Gerelateerd runbook bijwerken ([runbook-index.md](./runbook-index.md))
3. Top-3 patterns sync met [top-error-patterns.md](../product/top-error-patterns.md)

## Gesloten learnings (voorbeeld)

| ID | Afgerond | Resultaat |
|---|---|---|
| IL-001 | 2026-Q2 | Live chunk builder + fallback subdivisions |
| IL-002 | 2026-Q2 | Confidence score in API response |
