# Secret inventory — Lawyer RAG platform

| Secret | Env var | Class | Used by | Rotation |
|---|---|---|---|---|
| OpenRouter API key | `OPENROUTER_API_KEY` | API key | LLM queries | 90 dagen / bij leak |
| Anthropic API key | `ANTHROPIC_API_KEY` | API key | LLM fallback | 90 dagen / bij leak |
| OpenAI API key | `OPENAI_API_KEY` | API key | Embeddings (optioneel) | 90 dagen / bij leak |
| JWT signing secret | `JWT_SECRET` | Crypto | Auth tokens | 180 dagen / bij leak |
| Admin API key | `ADMIN_API_KEY` | API key | Admin endpoints | 90 dagen / bij leak |
| Grafana admin password | `GRAFANA_ADMIN_PASSWORD` | Password | Grafana UI | 90 dagen / bij leak |
| Postgres credentials | `DATABASE_URL` | Password | Backend, workers | 180 dagen / bij leak |
| Redis URL (if auth) | `REDIS_URL` | Password | Cache | 180 dagen / bij leak |
| EUR-Lex login | `EU_LOGIN_EMAIL`, `EU_LOGIN_PASSWORD` | Password | Bulk ingest | 180 dagen / bij leak |

## Storage rules

- **Development:** `.env` lokaal, nooit in git.
- **CI:** alleen GitHub Actions secrets (indien nodig), geen echte keys in workflow YAML.
- **Production:** secrets manager (Vault / Doppler / cloud SM) — geen plain `.env` op servers.

## Owners

| Domein | Owner rol |
|---|---|
| LLM / embedding keys | Platform engineer |
| JWT / admin keys | Security / backend lead |
| Database / Redis | DevOps |
| Grafana | Observability owner |
| EUR-Lex credentials | Data / ingest owner |

## Verification

```bash
./scripts/security/check-secrets.sh all
./scripts/security/check-log-output.sh
```

Zie ook: [secret-rotation-playbook.md](./secret-rotation-playbook.md), [incident-key-exposure.md](./incident-key-exposure.md).
