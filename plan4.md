# Implementatieplan Deel 4 - Enterprise hardening, governance en compliance

## Relatie met eerdere plannen

- Vorige plan: `plan3.md`
- Gebruik: dit plan borgt enterprise-kwaliteit, governance en auditability na schaalfase.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan5.md`.

## Waar zitten we nu

- [ ] `plan3.md` volledig afgerond
- [ ] Productiegedrag stabiel gedurende minimaal 2 weken
- [ ] Stakeholders akkoord op start hardeningfase

## Hoofddoelen plan4

- [ ] Security maturity verhogen
- [ ] Compliance en auditprocessen operationaliseren
- [ ] Release governance en change control professionaliseren

## Werkstroom E - Security verdieping

### E1. Toegangsbeheer en authz

- [ ] RBAC matrix op endpointniveau vastleggen
- [ ] Service-layer autorisatiechecks testen
- [ ] Admin debugfeatures afschermen
- [ ] Security regression suite opnemen in CI

### E2. Secret en key management

- [ ] Secret inventory compleet maken
- [ ] Rotatieprocedure oefenen (tabletop + test)
- [ ] Geen secrets in logs/build output controleren
- [ ] Incident playbook voor key exposure opstellen

### E3. Applicatiebeveiliging

- [ ] Input validatie coverage audit
- [ ] SSRF/Injection/XSS checks op fallback en parsing flow
- [ ] Dependency vulnerability scan in release-gates opnemen
- [ ] Pentest bevindingen verwerken

## Werkstroom F - Compliance en data governance

### F1. Data lifecycle

- [ ] Data-classificatie (PII, pseudo-PII, niet-PII) valideren
- [ ] Retentiebeleid technisch afdwingen
- [ ] Verwijderingsverzoeken proces documenteren
- [ ] Audit van bewaartermijnen uitvoeren

### F2. Audittrail en verantwoordbaarheid

- [ ] Auditlog completeness check (vraag, route, chunks, model)
- [ ] Onveranderbaarheid/log-integriteitstrategie bepalen
- [ ] Toegangsbeheer voor auditdata instellen
- [ ] Maandelijkse auditrapportage format vastleggen

### F3. Juridische en product disclaimers

- [ ] Disclaimer consistent in alle interfaces tonen
- [ ] Bronnenplicht afdwingen in antwoordtemplate
- [ ] Escalatiepad naar menselijke jurist beschrijven
- [ ] Uitzonderingen en beperkingen documenteren

## Werkstroom G - Release governance

### G1. Change management

- [ ] Release checklist standaardiseren
- [ ] Mandatory approvals per change-type vastleggen
- [ ] Hotfixproces met rollbacktimebox formaliseren
- [ ] Post-release review ritme inplannen

### G2. SLO/SLA governance

- [ ] SLO set bevestigen met product en operations
- [ ] Error budget proces inrichten
- [ ] Alert-fatigue review uitvoeren
- [ ] Escalatiematrix actualiseren

## KPI-doelen plan4

- [ ] 0 kritieke open security bevindingen
- [ ] 100% releasechecks gebruikt op productiechanges
- [ ] Auditrapportages elke maand volledig opgeleverd
- [ ] SLO adherence >= afgesproken niveau

## Exit criteria plan4

- [ ] Werkstromen E, F en G volledig afgerond
- [ ] Compliance en security sign-off behaald
- [ ] Operations en product hebben governanceproces geadopteerd
- [ ] Go voor `plan5.md` bevestigd

## Overdrachtsregel naar plan5

- [ ] Als alle onderdelen in dit document zijn afgevinkt, wordt verder gewerkt in `plan5.md`.
