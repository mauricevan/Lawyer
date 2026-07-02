# Review guild / chapter (plan8 S)

## Doel

Consistente codekwaliteit en kennisdeling — nu solo, uitbreidbaar naar team.

## Ritme

| Activiteit | Frequentie | Duur |
|---|---|---|
| Self-review (kritieke paden) | Per merge | 30 min |
| Architecture skim | Maandelijks | 45 min |
| Guild notes | Per kwartaal | 1 uur |

## Solo-protocol (nu)

1. Wacht 30 min na implementatie
2. Doorloop [pair-review-policy.md](./pair-review-policy.md) checklist
3. `PAIR_REVIEW_ACK=yes ./scripts/ops/check-pair-review.sh`
4. Noteer learnings in [incident-learnings.md](./incident-learnings.md) of ADR

## Bij teamgroei (≥2 engineers)

- **Rotating reviewer** per week per critical component
- **Guild meeting** — 1 uur: 1 deep-dive (RAG, security, ingest)
- **Shared backlog** voor review findings → debt register

## Onderwerpen backlog (voorbeeld)

- Retrieval language fallback gedrag
- Eval baseline update policy
- Prompt change control

## KPI

Meet via [onboarding-kpis.yaml](./onboarding-kpis.yaml) en kwartaalreview.
