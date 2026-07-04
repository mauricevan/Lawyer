# Troubleshooting guide — Lawyer RAG

Snelle diagnose: symptoom → eerste actie → runbook.

## Query & retrieval

| Symptoom | Eerste check | Runbook / fix |
|---|---|---|
| Leeg antwoord, geen bronnen | Logs `rag_service`, retrieval route | [top-5 #2](../../observability/runbooks/top-5-incidents.md) |
| Alleen live_fallback, lage score | `fallback_score_threshold`, EUR-Lex bereikbaar | [top-5 #2](../../observability/runbooks/top-5-incidents.md) |
| Verkeerde CELEX | Router filters, `legal_term_hints` | [top-error-patterns #4](../product/top-error-patterns.md) |
| Traag (>8s p95) | Redis cache, retrieval budget | [top-5 #3](../../observability/runbooks/top-5-incidents.md) |
| FR/DE/ES slechte resultaten | Taal in request, fallback chain | [language-fallback-matrix.md](../product/language-fallback-matrix.md) |

## Platform

| Symptoom | Eerste check | Runbook / fix |
|---|---|---|
| `/ready` 503 | Postgres, Qdrant, Redis status | [top-5 #1, #5](../../observability/runbooks/top-5-incidents.md) |
| 500 op stream/query na deploy | `alembic current` in container | `docker compose exec backend alembic upgrade head` |
| Frontend "Failed to fetch" | `NEXT_PUBLIC_API_URL`, CORS | Herstart frontend; check poort 8001 met local compose |
| Metadata mist na reload | Stream append zonder coverage velden | Update backend; verify `test_query_stream_emits_complete_event` |
| 401/403 op admin | `ADMIN_API_KEY`, JWT config | [secret-inventory.md](../security/secret-inventory.md) |
| Migratie faalt | `alembic current`, logs | `alembic upgrade head` op staging eerst |
| Celery jobs stuck | Worker logs, Redis | [top-5 #4](../../observability/runbooks/top-5-incidents.md) |

## Security

| Symptoom | Eerste check | Runbook / fix |
|---|---|---|
| Secret in commit | pre-commit hook output | [incident-key-exposure.md](../security/incident-key-exposure.md) |
| SSRF-verdachte URL | `ssrf_guard` logs | Rotate keys indien productie |
| Prompt injection poging | 422 `PROMPT_INJECTION_DETECTED` | Geen actie — guard werkt |

## Diagnose-commando's

```bash
curl -s localhost:8001/ready | jq .
curl -s localhost:8001/metrics | grep lawyer_query
docker compose logs backend --tail 80
pytest backend/tests/test_live_fallback_and_cache.py -q
./scripts/observability/verify-stack.sh
```

## Wanneer escaleren

- Data corruptie, security breach, >30 min downtime → [hotfix-runbook.md](../ops/hotfix-runbook.md) + [escalation-matrix.md](../ops/escalation-matrix.md)

## Na oplossing

1. Post-mortem notitie in [incident-learnings.md](./incident-learnings.md)
2. Runbook bijwerken indien nieuw patroon
3. Test toevoegen indien regressie-risico
