# Feedback triage — pilot

## Taxonomie

| Category | Label | Default rating | Prioriteit |
|---|---|---|---|
| `incorrect` | Onjuist | 1 | P0 |
| `source_issue` | Bronprobleem | 2 | P0 |
| `incomplete` | Onvolledig | 2 | P1 |
| `ux` | Gebruiksvriendelijkheid | 3 | P2 |
| `positive` | Positief | 5 | — |

## Prioriteringsregels → backlog

1. **P0** — `incorrect` of `source_issue` met rating ≤ 2 → ticket binnen 48 uur.
2. **P1** — `incomplete` of ≥3 meldingenzelfde categorie in 7 dagen → sprint backlog.
3. **P2** — `ux` → maandelijkse UX-review.
4. **Positief** — alleen metrics, geen ticket.

## Wekelijkse triage (verplicht)

Elke maandag 30 min:

- [ ] Export feedback uit DB (`query_feedback`, laatste 7 dagen)
- [ ] Groepeer op `category` en `conversation_id`
- [ ] Maak P0-tickets aan in backlog
- [ ] Noteer trends in weekly product note

## KPI

- Negatieve feedbackratio = (rating ≤ 3) / totaal
- Doel: dalende trend kwartaal-op-kwartaal (plan5)
