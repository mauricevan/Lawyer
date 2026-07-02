## Summary

<!-- What changed and why -->

## Test plan

- [ ] `pytest backend/tests -m "not integration" -q`
- [ ] `cd frontend && npm test -- --run`
- [ ] `./scripts/ops/run-knowledge-base-check.sh`

## Pair review (critical paths)

- [ ] Geen kritieke paden gewijzigd, **of**
- [ ] `./scripts/ops/check-pair-review.sh` + checklist in [pair-review-policy.md](docs/engineering/pair-review-policy.md) afgevinkt
- [ ] `PAIR_REVIEW_ACK=yes` gezet na review (solo-team)

Kritieke paden: zie [critical-components.yaml](docs/engineering/critical-components.yaml)
