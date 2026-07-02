# Input validation coverage

Coverage wordt geaudit via `backend/src/security/input_validation_registry.py`.

## Uitvoeren

```bash
./scripts/security/run-input-validation-audit.sh
```

## Gedekte controles

| Laag | Controle |
|---|---|
| Body | Pydantic schemas met `Field` constraints |
| Path | UUID / CELEX validatie op route params |
| Query | `PageLimit`, `PageOffset`, `SampleSize`, `TitleQuery` |
| Business | Guardrails + SSRF guard op live fetch |

## Exit criteria

- 100% endpoints in registry status `validated`
- CI job `security-scan` draait audit script
