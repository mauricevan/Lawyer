# Secret rotation playbook

Gebruik dit document voor geplande rotatie of na een vermoeden van blootstelling.

## Voorbereiding

1. Maak nieuwe secrets aan in de juiste omgeving (nooit hergebruiken tussen dev/staging/prod).
2. Plan een kort onderhoudsvenster als JWT of DB-credentials wijzigen.
3. Controleer dat niemand oude waarden in `.env` commits heeft gepusht: `./scripts/security/check-secrets.sh all`.

## Rotatiestappen per secret

### LLM keys (`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)

1. Genereer nieuwe key in provider dashboard.
2. Update secret store / `.env`.
3. `docker compose up -d --force-recreate backend celery-worker`
4. Stuur testquery via `/api/v1/query`.
5. Revoke oude key in provider dashboard.

### JWT (`JWT_SECRET`)

1. Genereer min. 64 random bytes: `openssl rand -hex 32`
2. Update secret in alle backend instances tegelijk.
3. Herstart backend — **alle bestaande tokens vervallen**.
4. Informeer gebruikers dat opnieuw inloggen nodig is.

### Admin (`ADMIN_API_KEY`)

1. Genereer nieuwe key: `openssl rand -hex 24`
2. Update `.env` + frontend admin key (sessionStorage).
3. Herstart backend; test `GET /api/v1/admin/stats` met nieuwe header.

### Database (`DATABASE_URL`)

1. Maak nieuwe DB-user of wijzig wachtwoord in Postgres.
2. Update `DATABASE_URL` op backend + workers.
3. Rolling restart: backend → celery workers.
4. Verifieer `/ready` = postgres ok.
5. Verwijder oude DB-user na grace period.

### Grafana (`GRAFANA_ADMIN_PASSWORD`)

```bash
docker exec lawyer-grafana-1 grafana-cli admin reset-admin-password '<nieuw>'
```

Update `GRAFANA_ADMIN_PASSWORD` in `.env` voor consistentie.

## Tabletop oefening

```bash
./scripts/security/run-rotation-tabletop.sh
```

Vink elke stap af zonder productie te wijzigen — alleen checklist doorlopen.

## Post-rotatie

- [ ] Oude secret gerevoked
- [ ] Geen errors in logs (`check-log-output.sh`)
- [ ] Health + query smoke test groen
- [ ] Incident ticket sluiten (indien van toepassing)
