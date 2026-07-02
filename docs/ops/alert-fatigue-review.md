# Alert fatigue review — kwartaalchecklist

Voer elke **3 maanden** uit of na > 3 valse positieven per week.

## Review vragen

- [ ] Elke actieve alert heeft een runbook-link
- [ ] Geen alert zonder `for:` debounce onder 2 minuten (behalve P0)
- [ ] Warning-alerts escaleren niet 's nachts zonder on-call rotatie
- [ ] Alerts gekoppeld aan [escalatiematrix.md](./escalatiematrix.md) severity

## Huidige alerts (`observability/prometheus/alerts.yml`)

| Alert | Actie nodig? | Notities |
|---|---|---|
| LawyerBackendDown | | |
| LawyerHighFallbackFailureRate | | |
| LawyerIngestEnqueueFailures | | |

## Outcome

- [ ] Alerts verwijderd/merged: ___
- [ ] Drempels aangepast: ___
- [ ] Nieuwe runbook-secties: ___
