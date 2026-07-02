# Non-strategic work wind-down (plan9 T)

## Definitie

Werk is **niet-strategisch** als:

- Score < `wind_down_threshold` in [prioritization-model.yaml](./prioritization-model.yaml)
- Geen koppeling aan actief objective in [portfolio-metrics.yaml](./portfolio-metrics.yaml)
- Status `pilot`/`no_go` > 2 kwartalen zonder metric verbetering

## Proces

1. **Identificeer** — portfolio board maakt lijst (max 5 items)
2. **Besluit** — freeze, merge, of verwijderen
3. **Communiceer** — update roadmap + domain registry status
4. **Meet** — volgend kwartaal: minder open P3 debt-items

## Voorbeelden Lawyer

| Item | Actie | Kwartaal |
|---|---|---|
| Competition domein `no_go` | Geen investering tot nieuwe cluster | Q3 freeze |
| Plan4 ad-hoc docs | Consolideer in plan5 scorecard | Done |
| Oude planN files zonder status | Archiveer of update checkbox | Doorlopend |

## Escalatie

Twijfel → ADR of architecture review; geen stille voortzetting.
