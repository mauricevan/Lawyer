# Acceptatie-voorbeelden — Declarant-stijl (referentie)

**Gebruik:** handmatige en automatische vergelijking — “lijkt het antwoord op dit?”  
**Parent:** [master-plan-declarant-workflow.md](./master-plan-declarant-workflow.md)

---

## Checklist (elk antwoord)

- [ ] Intake/context klopt
- [ ] Juiste CELEX (geen verkeerd domein)
- [ ] Artikelen uit opgehaalde chunks
- [ ] Letterlijke EUR-Lex-tekst aanwezig (geen synthetic)
- [ ] Lekentaal + EU/nationaal waar nodig
- [ ] Onzekerheden benoemd
- [ ] Geen `Marktdeelnemers onder … governance, transparantie`
- [ ] Geen lege `CELEX ,`

---

## Voorbeeld Douane

**Vraag:** Webshop, pakketjes vanuit China naar NL, onder €150 — douaneaangifte?

**Minimaal in antwoord:**

- Kort: invoer = douane-procedure; kleine waarde ≠ automatisch vrij
- CELEX **32013R0952** (UDW), art. 156-ruimte
- Officiële tekst-collapsible uit echte chunks
- Onzekerheid: wie is importeur, IOSS, productcategorie
- **Niet:** Consumer Rights, AVG, placeholder-tekst

---

## Voorbeeld Legitimatie

**Vraag:** Moet ik me in de EU kunnen legitimeren? → **overheidsdienst / formulier**

**Minimaal in antwoord:**

- Kort: deels EU (eIDAS, vrij verkeer), deels nationaal
- CELEX **32014R0910**, **32004L0038** — **niet** 32011L0083
- Tabel EU vs nationaal
- Officiële tekst art. 5 lid 1 (2004/38) indien opgehaald
- **Niet:** “Marktdeelnemers onder Consumer Rights”

---

## Voorbeeld Platform

**Vraag:** mag ik een platform bouwen → **contentwebsite**

**Minimaal in antwoord:**

- Kort: DSA-plichten voor hosting/platform
- CELEX **32022R2065**
- `coverage_status: adequate` bij goede chunks
- **Niet:** Consumer Rights gap na chip

---

## Automatische forbidden patterns

Tests moeten falen als antwoord bevat:

```
Marktdeelnemers onder
governance, transparantie, rapportage
CELEX ,
Consumer Rights.*legitim
32011L0083.*legitim
```

---

## Product-owner steekproef (5 vragen)

1. Douane webshop import (C1)
2. Legitimatie EU + overheid (I1)
3. Platform contentwebsite (D1)
4. AVG data opslaan (D2)
5. Vervolgvraag: “in welke wetgeving staat dat?” op I1

**Goed:** jij zou het zo aan een klant kunnen sturen (met disclaimer).  
**Niet goed:** je zou als declarant zeggen “dit kan ik niet zo uit de wet halen” — maar het platform gaf toch antwoord.
