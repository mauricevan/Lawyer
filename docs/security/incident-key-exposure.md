# Incident playbook — key exposure

## Wanneer activeren

- Secret in git commit, PR, log, screenshot of publieke channel
- Verdachte API-gebruik op LLM provider dashboard
- Melding van security tool of teamlid

## Eerste 15 minuten

1. **Bevestig scope** — welke secret(s), welke omgeving, sinds wanneer?
2. **Contain** — revoke/roteer getroffen keys onmiddellijk (zie rotation playbook).
3. **Stop bleeding** — revert commit indien secret in git; `git filter-repo` alleen met teamafstemming.
4. **Blokkeer misbruik** — rate limits / IP allowlist indien beschikbaar.

## Communicatie

| Rol | Actie |
|---|---|
| Engineer on-call | Rotatie + smoke tests |
| Tech lead | Impact inschatting |
| Product / legal | Klantcommunicatie indien PII betrokken |

## Onderzoek

- Doorzoek logs op misbruik (OpenRouter usage, failed auth spikes).
- Run `./scripts/security/check-secrets.sh all` op repo.
- Documenteer timeline in incident ticket.

## Herstel checklist

- [ ] Alle getroffen secrets geroteerd
- [ ] Oude credentials revoked
- [ ] Geen secrets meer in git history (of mitigatie gedocumenteerd)
- [ ] Smoke tests: health, query, admin, Grafana
- [ ] Post-mortem binnen 5 werkdagen

## Preventie (follow-up)

- Pre-commit hook actief: `./scripts/security/install-hooks.sh`
- CI `secret-scan` job moet groen blijven
- Geen secrets in `docker compose` command line args
