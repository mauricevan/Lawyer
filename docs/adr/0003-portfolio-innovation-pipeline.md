# ADR-0003: Portfolio prioritization and innovation pipeline

**Status:** Accepted  
**Date:** 2026-07-02  
**Context:** Plan9 vereist data-gedreven prioritering en gecontroleerde innovatie.

## Decision

1. **Scoring** via `PortfolioScoringService` + `prioritization-model.yaml`.
2. **Portfolio board** ritme gedocumenteerd; gate via `run-portfolio-board-review.sh`.
3. **Experimenten** in `experiment-backlog.yaml` met hypothese en stop/go; budget in `innovation-budget.yaml`.
4. **Strategische risico's** in `strategic-risk-register.yaml` met kwartaalreview script.

## Consequences

- Initiatieven onder wind-down threshold worden niet gepland zonder ADR.
- Max 2 actieve experimenten in solo-capaciteit.
- Hoge exposure risks (≥12) vereisen architecture review.
