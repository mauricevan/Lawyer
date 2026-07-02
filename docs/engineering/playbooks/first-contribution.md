# Playbook: eerste bijdrage (plan8 S)

## Doel

Productieve eerste merge binnen **2 werkdagen**.

## Stappen

### 1. Omgeving (dag 1)

Volg [onboarding.md](../onboarding.md) setup + verificatietabel.

### 2. Kleine wijziging kiezen

- Doc-fix of test-fix aanbevolen
- Geen kritieke componenten in eerste PR
- Branch: `fix/onboarding-typo` of `docs/clarify-readme`

### 3. Implementeren

```bash
git checkout -b fix/my-first-change
# wijziging + test
pytest backend/tests -m "not integration" -q
```

### 4. Definition of Done

Doorloop [definition-of-done.md](../definition-of-done.md).

### 5. Merge

```bash
git push -u origin HEAD
# PR of direct main per team policy
```

## Succescriteria

- [ ] CI groen
- [ ] Ten minste één test toegevoegd of bijgewerkt
- [ ] Reviewer (of self-review) checklist afgevinkt
