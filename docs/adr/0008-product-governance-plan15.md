# ADR-0008: Plan15 product governance focus

**Status:** Accepted  
**Date:** 2026-07-03  
**Context:** Plan14 closed with enterprise reliability gates. Buyers and auditors require traceable policy decisions beyond operational runbooks.

## Decision

1. **Plan15** prioritizes product governance and policy automation over new retrieval features.
2. **Policy-as-code** centralizes rollout, legal, and risk rules in validated YAML registries.
3. **Risk acceptance** uses a structured workflow with immutable decision log entries.
4. **Governance reporting** surfaces policy compliance in admin and release gates.

## Consequences

- New policy registries live under `shared/config/` with matching validation gates.
- Breaking changes to admin stats require schema update in shared types.
- Feature work deferred unless tied to governance or audit requirements.
