# Portfolio board cadence (plan9 T)

## Ritme

| Meeting | Frequentie | Duur | Output |
|---|---|---|---|
| Portfolio board | Eerste maandag kwartaal | 60 min | Roadmap lock |
| Mid-quarter review | Week 6 | 45 min | Capacity bijsturing |
| Architecture review | Laatste week kwartaal | 90 min | ADR's + debt done |
| Weekly triage | Wekelijks (15 min) | 15 min | Top-3 focus |

## Agenda portfolio board

1. Objectives vs targets ([portfolio-metrics.yaml](./portfolio-metrics.yaml))
2. Score initiatieven ([prioritization-model.yaml](./prioritization-model.yaml))
3. Wind-down niet-strategisch werk ([non-strategic-winddown.md](./non-strategic-winddown.md))
4. Lock [quarterly-roadmap.md](./quarterly-roadmap.md)

## Solo-team

Eén persoon doorloopt agenda als checklist; besluiten loggen in roadmap + ADR.

## Gate script

```bash
./scripts/ops/run-portfolio-board-review.sh
```

Koppeling: [run-quarterly-portfolio-review.sh](../../scripts/ops/run-quarterly-portfolio-review.sh)
