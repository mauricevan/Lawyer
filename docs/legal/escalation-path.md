# Escalatiepad — menselijke jurist

**Validatie:** `./scripts/qa/run-legal-compliance-check.sh` (plan11 AC)

## Wanneer escaleren

- Bindende beslissingen (contracten, toezicht, geschillen)
- Conflicterende bronnen of onduidelijke versie-inwerkingtreding
- Nationale implementatie of sector-specifieke regels buiten de getoonde context — zie [national-implementation-gaps.md](./national-implementation-gaps.md)

## Stappen

1. **Verifieer bronnen** op EUR-Lex (geconsolideerde versie, inwerkingtreding).
2. **Documenteer** welke CELEX/artikelen zijn gebruikt (export PDF/DOCX).
3. **Escaleer** naar interne legal counsel of externe advocaat met vraag + bronnen.
4. **Meld** systematische fouten via feedback (categorie: bronprobleem/onjuist).

## SLA intern (pilot)

| Ernst | Actie | Termijn |
|---|---|---|
| P0 incorrect/bron | Ticket + legal review | 48 uur |
| P1 onvolledig | Backlog triage | 1 week |
| UX | Maandelijkse review | — |

Zie ook: [product-limitations.md](./product-limitations.md)
