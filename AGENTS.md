# AI AGENT CODE MANIFEST

> Niet onderhandelen. Dit is hoe wij bouwen.
>
> Versie 1.1 — Vastgesteld door de CEO

---

## 0. MINDSET — Begrijp dit of begin er niet aan

Elke regel code die jij schrijft representeert dit bedrijf. Slechte code kost geld. Technische schuld doodt bedrijven. Jij bent geen typemachine — jij bent een engineer met verantwoordelijkheid. Denk eerst. Schrijf daarna.

**Context window beheer (verplicht voor elke taak):** Voer een context compact uit als de resterende context onder de **20% van het maximum** zakt, of als de taakgeschiedenis langer is dan **15 berichten** zonder tussentijdse samenvatting. Controleer dit actief vóór je een nieuwe taak begint — niet erna.

Indien een taak gedaan is en goed met bewijs getest is, maak een commit naar GitHub.

---

## 1. BESTANDSSTRUCTUUR & GROOTTE

- Maximaal **250 regels** per bestand. Geen uitzonderingen — tenzij het een puur declaratief configuratie- of tokenbestand betreft (bijv. `tokens.css`, `.env.example`). Voor dat type bestand geldt een maximum van **400 regels**, mits het bestand geen logica bevat.
- Splits een bestand op als het richting 200 regels gaat — wacht niet op 250.
- Eén bestand = één verantwoordelijkheid (Single Responsibility Principle).
- Gebruik altijd een logische mappenstructuur voor je begint:

```
/src
  /components      ← UI-bouwstenen
  /services        ← business logica & API-calls
  /utils           ← herbruikbare hulpfuncties
  /models          ← datastructuren & types
  /tests           ← alle testbestanden
/docs
  /engineering     ← incident-learnings.md, pair-review-policy.md
/config            ← omgevingsinstellingen
/styles
  tokens.css       ← uitzondering: mag tot 400 regels (puur declaratief)

```

- Geen "rommelbestanden" zoals `helpers2.js`, `final_v3_echt_nu.py`. Nooit.

---

## 2. CODE HERGEBRUIK — DRY IS WET GELD

"Don't Repeat Yourself" is geen suggestie. Het is financieel beleid.

- Schrijf je iets voor de tweede keer? Stop. Maak een functie.
- Schrijf je iets voor de derde keer? Stop. Maak een module.
- Controleer altijd eerst of er al een utility/service/component bestaat voordat je iets nieuws schrijft.
- Deel gedeelde logica op in `/utils` of `/services` — nooit inline herhalen.
- Gebruik bestaande libraries voor standaardproblemen (datums, validatie, HTTP). Het wiel wordt niet opnieuw uitgevonden in dit bedrijf.

---

## 3. NAAMGEVING — Als je het niet kunt uitleggen, geef het een andere naam

- Variabelen, functies en klassen krijgen beschrijvende namen in het **Engels**.
- Geen: `x`, `data2`, `tmpResult`, `doStuff()`, `handleThings()`
- Wel: `calculateMonthlyRevenue()`, `userAuthToken`, `parseInvoiceItems()`
- Boolean variabelen starten altijd met `is`, `has`, of `can`: `isLoading`, `hasPermission`
- Functies zijn werkwoorden: `fetchUser()`, `validateEmail()`, `renderDashboard()`
- Klassen/Components zijn zelfstandige naamwoorden: `UserService`, `InvoiceModel`
- Consistentie per taal: `camelCase` (JS/TS), `snake_case` (Python), `PascalCase` (classes overal)

---

## 4. FUNCTIES — Klein, scherp, één doel

- Een functie doet **één ding**. Als je "en" gebruikt om het te beschrijven, splits dan.
- Maximaal **20 regels** per functie. Meer = heroverweeg de opzet.
- Maximaal **3 parameters**. Meer nodig? Gebruik een object/struct.
- Pure functies verdienen de voorkeur: zelfde input → zelfde output, geen verborgen bijwerkingen.
- Functies die kunnen falen retourneren expliciete errors, gooien ze niet stilletjes weg.

---

## 5. HIËRARCHIE & ARCHITECTUUR

Elke codebase volgt 3 lagen. Niet meer, niet minder:

```
┌─────────────────────────────┐
│  PRESENTATIE (UI / Output)  │  ← Wat de gebruiker ziet
├─────────────────────────────┤
│  LOGICA (Services / Rules)  │  ← Wat het systeem doet
├─────────────────────────────┤
│  DATA (Models / Storage)    │  ← Wat het systeem onthoudt
└─────────────────────────────┘

```

Lagen spreken alleen met hun directe buur. UI roept nooit direct de database aan. Schending van dit principe = onmiddellijk refactoren voordat verder wordt gegaan.

---

## 6. CODE REVIEW — Vier ogen zien meer dan twee

Elke substantiële wijziging doorloopt deze checklist voordat het gecommit wordt:

### ✅ Zelf-review (verplicht, altijd)

- [ ] Voldoet de code aan de regellimiet per bestand (250 / 400 voor tokens)?
- [ ] Is er dubbele logica die kan worden samengetrokken?
- [ ] Zijn alle functies kleiner dan 20 regels?
- [ ] Zijn namen beschrijvend en consistent?
- [ ] Is foutafhandeling aanwezig voor alle externe calls?
- [ ] Zijn er geen hardcoded waarden (wachtwoorden, URLs, magic numbers)?
- [ ] Is de code leesbaar zonder extra uitleg nodig te hebben?

### 🔍 Architectuur-check

- [ ] Volgt de code de 3-lagenstructuur?
- [ ] Is de nieuwe code op de juiste plek in de mappenstructuur?
- [ ] Zijn er geen cirkelvormige afhankelijkheden geïntroduceerd?

---

## 7. TESTEN — Code zonder tests is een belofte zonder garantie

Geen test = geen productie. Dit is geen beleid, dit is zelfrespect.

**Teststrategie (verplicht):**

- Unit tests voor elke utility-functie en service-methode
- Integratietests voor elke API-endpoint en datasource-connectie
- Edge case tests: lege input, null-waarden, extreme getallen, verkeerde datatypes

**Minimale testdekking:**


| Laag              | Minimaal |
| ----------------- | -------- |
| Utils / Helpers   | 90%      |
| Services / Logica | 80%      |
| API Endpoints     | 75%      |
| UI Components     | 60%      |


**Backend minimale testdekking** (aanvullend op bovenstaande):


| Laag                          | Minimaal |
| ----------------------------- | -------- |
| Service-laag (business logic) | 85%      |
| Repository / Data access      | 75%      |
| API Controllers / Routes      | 75%      |
| Auth & Authorization paths    | 90%      |


**Testregel:**

- Testbestand staat altijd naast of in `/tests` met dezelfde naam + `.test` of `_test`
- Tests draaien lokaal groen voordat iets gecommit wordt
- Een falende test is een stopbord, geen gele kaart

---

## 8. FOUTAFHANDELING — Plan voor het ergste, bouw voor het beste

- Elke externe call (API, database, bestandssysteem) krijgt expliciete foutafhandeling
- Foutmeldingen zijn menselijk leesbaar én debugbaar (log de context, niet alleen "Error occurred")
- Gebruik geen lege catch-blokken: `catch(e) {}` is een misdaad
- Onderscheid verwachte fouten (gebruikersinvoer) van onverwachte fouten (systeemstoringen)
- Kritieke fouten worden gelogd met timestamp, context en stack trace

---

## 9. DOCUMENTATIE — Code vertelt wat. Documentatie vertelt waarom.

- Elk bestand begint met een korte header: wat doet dit, wie is de eigenaar, wanneer aangemaakt.
- Elke publieke functie krijgt een docstring/JSDoc met: doel, parameters, return-waarde.
- Complexe logica krijgt een inline comment boven de betreffende regels.
- Een `README.md` per module die uitlegt: doel, hoe te gebruiken, dependencies.
- Nooit verouderde comments laten staan. Stale comments zijn erger dan geen comments.

---

## 10. SECURITY — Vertrouw niemand, ook niet jezelf

- Nooit API-keys, wachtwoorden of tokens in code of git. Altijd `.env` + `.gitignore`.
- Valideer altijd alle input van buiten — gebruiker, API, bestand, alles.
- Principle of Least Privilege: een module krijgt alleen toegang tot wat hij écht nodig heeft.
- Gebruikersdata wordt nooit gelogd in plain text.
- Dependencies worden wekelijks gescand op bekende kwetsbaarheden (`npm audit`, `pip-audit`).

---

## 11. PERFORMANCE — Snel is een feature

- Optimaliseer nooit prematuur — bouw eerst correct, meet dan, optimaliseer daarna.
- Grote datasets worden gepagineerd of gestreamd — nooit in één keer in geheugen geladen.
- Database-queries krijgen altijd een index-analyse bij meer dan 1.000 records.
- Frontend-componenten worden alleen gerenderd als hun data verandert.
- Zware operaties draaien asynchroon — de gebruiker wacht nooit zonder feedback.

---

## 12. GIT DISCIPLINE — Geschiedenis is documentatie

- Commitberichten zijn beschrijvend: `feat: add invoice pagination`, `fix: null check in user auth`
- Gebruik het **Conventional Commits** formaat: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Eén commit = één logische wijziging. Geen "WIP dump"-commits naar main.
- Feature branches altijd. Nooit rechtstreeks op `main` of `develop` pushen.
- Branch-naamgeving: `feature/`, `fix/`, `refactor/`, `docs/`

**Branch protection (verplicht voor productie-repos):**

- `main` en `develop` zijn beschermde branches — directe pushes zijn geblokkeerd.
- Mergen naar `main` vereist: minimaal 1 goedgekeurde pull request review + groene CI.
- CI moet volledig groen zijn (tests, linter, type checks) vóór merge. Rood = geen merge.
- Gebruik **squash merges** voor feature branches zodat de main-history leesbaar blijft.
- Hotfixes gaan via `fix/` branch + versneld PR-proces, niet via directe push.

---

## 13. AGENT-SPECIFIEKE REGELS — Jij bent AI. Gedraag je ernaar.

Deze sectie is speciaal voor jou, agent. Lees hem dubbel.

- **Vraag bij twijfel.** Aannames zijn de moeder van alle bugs. Als de opdracht niet 100% helder is, vraag dan om verduidelijking vóór je begint.
- **Werk incrementeel.** Lever kleine, werkende stukken op. Geen monolithische dumps van 500 regels.
- **Verwijder nooit bestaande code** zonder het expliciet te vermelden en te motiveren.
- **Geen magic numbers.** `const MAX_RETRIES = 3` — niet `if (retries > 3)`.
- **Controleer altijd** of de code die je schrijft past in het bestaande architectuurpatroon.
- **Test je eigen output.** Schrijf de test, draai hem mentaal door, lever dan de code.
- **Als iets niet kan worden opgelost** binnen de regels van dit manifest — meld het, los het niet stilletjes op op een slechte manier.
- **Refactor als je slechte code ziet**, ook als het niet de opdracht was. We laten geen puinhoop achter.

**Escalatieprotocol voor de agent:** Als je vastloopt op een technische keuze die dit manifest niet dekt, of als twee regels uit dit manifest elkaar tegenspreken in jouw specifieke situatie:

1. Benoem het probleem expliciet in je response — beschrijf de spanning of het gat.
2. Presenteer maximaal twee opties met hun trade-offs.
3. Wacht op een beslissing van de engineer/CEO voordat je verdergaat.
4. Documenteer de genomen beslissing als inline comment of in de relevante `README.md`. Stilzwijgend een keuze maken bij fundamentele onzekerheid is niet toegestaan.

### 13.1 Incident learnings (plan5 J2)

Vóór wijzigingen aan retrieval, auth, of live fallback: lees `docs/engineering/incident-learnings.md`.

> ⚠️ **Dit bestand moet bestaan voordat deze sectie geldig is.** Als `docs/engineering/incident-learnings.md` of `docs/engineering/pair-review-policy.md` nog niet aanwezig zijn in de repo, maak ze dan aan als eerste stap — met minimale boilerplate — zodat verwijzingen ernaar niet dood zijn.

- **Live EUR-Lex:** verifieer usable content — geen antwoord op lege 202/HTML.
- **Retrieval onzeker:** confidence + verificatievragen; geen bron = disclaimer + escalatie.
- **Externe URLs:** alleen via `ssrf_guard` allowlist.
- **Secrets:** nooit in git; pre-commit scan moet groen blijven.
- **Kritieke paden:** pair review volgens `docs/engineering/pair-review-policy.md`.

Nieuwe incident-lessen → tabel in `incident-learnings.md` + runbook-update indien nodig.

---

## 14. DEFINITIE VAN "KLAAR"

Een taak is pas klaar als:

- [ ] Code voldoet aan alle regels van dit manifest
- [ ] Alle relevante tests zijn geschreven én groen
- [ ] Geen linter-fouten of -waarschuwingen
- [ ] Code is self-review'd via checklist in sectie 6
- [ ] Documentatie is bijgewerkt
- [ ] Commit staat op de juiste branch met correct bericht

**Niet klaar = niet klaar. Er is geen "95% klaar".**

---

---

# FRONTEND DESIGN SPECIFICATIE

## Het Handvest van de Drie Disciplines

> Dit document is het fundament. Geen regel code wordt geschreven voordat elk onderdeel hiervan is doorgelezen, begrepen en geaccordeerd.

---

## DEEL 1 — GEDRAGSPSYCHOLOGIE

### 1.1 Cognitieve belasting (Cognitive Load)

- Het werkgeheugen van een gebruiker kan maximaal 5–9 elementen tegelijk verwerken (Miller's Law). Beperk de zichtbare keuzes per schermgebied strikt.
- Gebruik **chunking**: groepeer gerelateerde informatie visueel zodat de hersenen patronen herkennen.
- Vermijd informatiedichtheid: een scherm vol tekst, icoontjes en CTA-knoppen veroorzaakt keuzeverlamming. Elke pagina heeft één primair doel.
- Gebruik de **Hick-Hyman Law**: hoe meer keuzes, hoe langer de beslissingstijd. Minimaliseer navigatie-opties, formuliervelden en menu-items.

### 1.2 Visuele aandacht en scangedrag

- Gebruikers lezen niet — ze scannen in een F-patroon (desktop) of lineair van boven naar beneden (mobiel).
- Plaats de meest kritische informatie in de bovenste 200px van het scherm (above the fold).
- Gebruik witruimte actief: een leeg vlak trekt de blik naar het naastgelegen element.
- Contrast bepaalt wat gezien wordt. Het belangrijkste element op de pagina heeft het hoogste contrast met zijn achtergrond.
- Gebruik grootte-hiërarchie: de grootste tekst/het grootste element krijgt als eerste aandacht.

### 1.3 Vertrouwen en geloofwaardigheid

- Consistentie bouwt vertrouwen. Elementen die er hetzelfde uitzien, gedragen zich ook hetzelfde — altijd.
- Micro-interacties geven de gebruiker het gevoel dat het systeem reageert en leeft.
- Vermijd dark patterns. Dit vernietigt vertrouwen permanent.
- Feedback moet onmiddellijk zijn. Als een actie langer dan 200ms duurt, geef een visuele bevestiging.

### 1.4 Emotie en kleur


| Kleur     | Psychologische associatie         | Gebruik                              |
| --------- | --------------------------------- | ------------------------------------ |
| Blauw     | Vertrouwen, rust, betrouwbaarheid | Banken, SaaS, gezondheidszorg        |
| Groen     | Groei, veiligheid, succes         | Bevestigingen, duurzaamheid, finance |
| Rood      | Urgentie, gevaar, energie         | Foutmeldingen, uitverkoop-CTA's      |
| Oranje    | Vriendelijkheid, actie, warmte    | CTA-knoppen, jonge doelgroepen       |
| Paars     | Luxe, creativiteit, mysterie      | Premium producten, mode              |
| Zwart     | Autoriteit, elegantie, luxe       | High-end merken                      |
| Wit/Grijs | Neutraliteit, ruimte, helderheid  | Achtergronden, adempauzes            |


Kleur is nooit de enige informatiedrager. Combineer altijd kleur met vorm, tekst of icoon. Gebruik maximaal **3 kleuren** in de primaire UI (primair, accent, neutraal).

### 1.5 Toegankelijkheid als ethische plicht

- Toegankelijkheid is geen feature — het is het minimum.
- Houd de **WCAG 2.1 AA** standaard aan als absoluut minimum; streef naar AAA waar mogelijk.
- Ontwerp voor toetsenbordnavigatie: elke interactieve functie bereikbaar zonder muis.
- Focus-states zijn altijd zichtbaar — verwijder nooit `outline` zonder gelijkwaardig alternatief.

---

## DEEL 2 — VISUEEL ONTWERP

### 2.1 Kleurensysteem

```css
--color-primary:        [merkkleur, meest prominent]
--color-primary-hover:  [10–15% donkerder]
--color-accent:         [contrasterende accentkleur]
--color-bg:             [achtergrond pagina]
--color-surface:        [achtergrond kaarten/panels]
--color-border:         [subtiele scheidingslijnen]
--color-text-primary:   [hoofdtekst]
--color-text-secondary: [subtekst, labels]
--color-text-disabled:  [uitgeschakelde elementen]
--color-success:        [groen-tint]
--color-warning:        [geel/oranje-tint]
--color-error:          [rood-tint]
--color-info:           [blauw-tint]

```

- Geen hardcoded hexwaarden in componenten — altijd CSS custom properties.
- Lichte modus én donkere modus worden tegelijkertijd ontworpen, nooit achteraf.
- Contrastverhouding: minimaal 4.5:1 (normaal), 3:1 (grote tekst ≥18px bold of ≥24px).

### 2.2 Typografie

```css
--font-display:  [karaktervol display-font, spaarzaam]
--font-body:     [leesbaar body-font, ≥16px basis]
--font-mono:     [monospace voor code/data]

--text-xs:   0.75rem
--text-sm:   0.875rem
--text-base: 1rem       ← minimale bodytekst
--text-md:   1.125rem
--text-lg:   1.25rem
--text-xl:   1.5rem
--text-2xl:  1.875rem
--text-3xl:  2.25rem
--text-4xl:  3rem
--text-5xl:  3.75rem

```

- Nooit minder dan 16px voor bodytekst.
- Regellengte maximaal 65–75 tekens per regel.
- Regelafstand: 1.5 voor body, 1.2 voor koppen.
- Maximaal **2 lettertypefamilies** per project.

### 2.3 Spatiëring en grid

```css
--space-1:   4px    --space-6:  24px
--space-2:   8px    --space-8:  32px
--space-3:  12px    --space-10: 40px
--space-4:  16px    --space-12: 48px
--space-5:  20px    --space-16: 64px
                    --space-20: 80px
                    --space-24: 96px

```

- Desktop: 12-kolommen grid, 24px gutter, max-breedte 1280px of 1440px.
- Tablet: 8 kolommen, 20px gutter.
- Mobiel: 4 kolommen, 16px gutter, 16px marge links/rechts.

### 2.4 Componenten — visuele standaarden

**Knoppen**

- Primaire knop: hoge contrast, merkkleur, duidelijke hover/active-state
- Secundaire knop: outline of ghost, subtiel
- Tertiaire knop: tekst-only
- Destructieve knop: rood, altijd met bevestigingsdialoog
- Minimaal klikoppervlak: **44×44px**

**Formuliervelden**

- Hoogte: minimaal 44px op mobiel, 40px op desktop
- Label: altijd zichtbaar boven het veld, nooit alleen placeholder
- Foutmelding: direct onder het veld, rood + icoon + beschrijvende tekst

**Kaarten**

- Consistente padding: `--space-6` of `--space-8`
- Schaduw: licht en subtiel

### 2.5 Iconen

- Gebruik één iconensysteem — niet mengen.
- Minimale icoongrootte: 24×24px voor interactieve elementen.
- Iconen nooit alleen als informatie — combineer altijd met label of tooltip.

---

## DEEL 3 — FRONTEND ENGINEERING

### 3.1 Responsive design

```css
/* Default: mobiel (320px–767px) */
@media (min-width: 768px)  { /* tablet */ }
@media (min-width: 1024px) { /* laptop */ }
@media (min-width: 1280px) { /* desktop */ }
@media (min-width: 1536px) { /* wide desktop */ }

```

**Verboden:**

- ❌ Vaste px-breedtes op containers zonder max-width
- ❌ Horizontale scroll op enig schermformaat
- ❌ Hover-only functionaliteit

**Verplicht:**

- ✅ `box-sizing: border-box` globaal
- ✅ Alle tekstgroottes in `rem`
- ✅ Testen op minimaal 320px breedte

### 3.2 Flexibele typografie

```css
h1   { font-size: clamp(1.75rem, 4vw + 1rem, 3.5rem); }
h2   { font-size: clamp(1.375rem, 3vw + 0.75rem, 2.5rem); }
body { font-size: clamp(1rem, 1.5vw + 0.5rem, 1.125rem); }

```

### 3.3 Layout — geen overflow

```css
*, *::before, *::after { box-sizing: border-box; }
html, body { overflow-x: hidden; max-width: 100%; }
img, video, canvas, svg { max-width: 100%; display: block; }
p, li, h1, h2, h3, h4, h5, h6 { overflow-wrap: break-word; hyphens: auto; }

```

### 3.4 Performance — Core Web Vitals


| Metric | Doel           |
| ------ | -------------- |
| LCP    | < 2.5 seconden |
| INP    | < 200ms        |
| CLS    | < 0.1          |
| TTFB   | < 800ms        |
| FCP    | < 1.8 seconden |


### 3.5 CSS-architectuur

```
/styles
  ├── tokens.css          ← design tokens (uitzondering: max 400 regels)
  ├── reset.css
  ├── typography.css
  ├── layout.css
  ├── components/
  │   ├── button.css
  │   ├── form.css
  │   ├── card.css
  │   └── navigation.css
  ├── pages/
  └── utilities.css

```

### 3.6 Animatie

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

```

- Duur: 150–300ms voor micro-interacties, 300–500ms voor grotere overgangen.
- GPU-animaties uitsluitend via `transform` en `opacity`.

### 3.7 Donkere modus

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f0f;
    --color-surface: #1a1a1a;
    --color-text-primary: #f5f5f5;
  }
}
[data-theme="dark"] { --color-bg: #0f0f0f; }

```

- Gebruik geen puur zwart (`#000000`) — gebruik donker grijs (`#0f0f0f` tot `#1a1a1a`).
- Schaduwen werken niet op donkere achtergronden — vervang door subtiele borders.

---

## DEEL 4 — NAVIGATIE EN GEBRUIKERSSTROOM

- Maximaal 7 items in de hoofdnavigatie.
- Actieve pagina altijd visueel gemarkeerd.
- Mobiel: bottom navigation bar heeft voorkeur bij ≤5 items.

```css
html { scroll-behavior: smooth; }
nav  { position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }
[id] { scroll-margin-top: 80px; }

:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

```

---

## DEEL 5 — FORMULIEREN EN FEEDBACK

- Één kolom op mobiel — altijd.
- Bewaar formulierstatus bij fout — leeg een formulier nooit volledig.
- Elke actie heeft vier staten: **Idle → Loading → Success → Error**

**Laadtijddrempels:**

- < 100ms → geen indicator
- 100–300ms → subtiele spinner
- 300ms–1s → prominente spinner
- 

> 1 seconde → progress bar of skelet-scherm

- 

> 10 seconden → annuleringsoptie aanbieden

---

## DEEL 6 — TESTPROTOCOL

### 6.1 Apparaattesten

- iPhone SE (375px), iPhone 14/15 (390px), Samsung Galaxy S (360px)
- iPad (768px), iPad Pro (1024px)
- Desktop: 1280px, 1440px, 1920px, 2560px
- **Minimum: 320px — geen horizontale scroll toegestaan**

### 6.2 Toegankelijkheidstest

- [ ] Axe DevTools — Lighthouse Accessibility score ≥ 90
- [ ] Volledige toetsenbordnavigatie doorlopen
- [ ] Schermlezer-test
- [ ] Ingezoomd op 200% — geen overflow

### 6.3 Performance

- [ ] Lighthouse Performance ≥ 90 (mobiel)
- [ ] LCP < 2.5s, CLS < 0.1, INP < 200ms
- [ ] Geen afbeeldingen > 200KB zonder rechtvaardiging

---

## DEEL 7 — DESIGN TOKENS TEMPLATE

```css
:root {
  --color-primary:           #000000; /* INVULLEN */
  --color-primary-hover:     #000000;
  --color-accent:            #000000;
  --color-bg:                #ffffff;
  --color-surface:           #f8f8f8;
  --color-border:            #e5e5e5;
  --color-text-primary:      #111111;
  --color-text-secondary:    #555555;
  --color-text-disabled:     #aaaaaa;
  --color-success:           #16a34a;
  --color-warning:           #d97706;
  --color-error:             #dc2626;
  --color-info:              #2563eb;

  --font-display:  'INVULLEN', sans-serif;
  --font-body:     'INVULLEN', sans-serif;
  --font-mono:     'INVULLEN', monospace;

  --space-1: 0.25rem;  --space-6:  1.5rem;
  --space-2: 0.5rem;   --space-8:  2rem;
  --space-3: 0.75rem;  --space-10: 2.5rem;
  --space-4: 1rem;     --space-12: 3rem;
  --space-5: 1.25rem;  --space-16: 4rem;

  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-full: 9999px;

  --duration-fast:   150ms;
  --duration-normal: 250ms;
  --duration-slow:   400ms;
  --ease-out:   cubic-bezier(0, 0, 0.2, 1);
  --ease-in:    cubic-bezier(0.4, 0, 1, 1);
  --ease-inout: cubic-bezier(0.4, 0, 0.2, 1);

  --z-dropdown: 100;
  --z-sticky:   200;
  --z-overlay:  300;
  --z-modal:    400;
  --z-toast:    500;
  --z-tooltip:  600;
}

```

---

---

# BACKEND AI AGENT — ENGINEERING STANDARDS

> Issued by the CEO. These rules are absolute. No exceptions. No shortcuts. No "I'll fix it later."

---

## 0. Mindset

You are not building a prototype. Every decision must assume real users, active attackers, future maintainers, and production uptime.

---

## 1. Security

### 1.1 Authentication & Authorization

- Every endpoint protected by default. Unauthenticated endpoints are explicit, documented exceptions.
- Authorization checks happen in the service/controller layer — never assume the caller is trusted.
- Short-lived tokens (JWT). Refresh tokens in HttpOnly cookies — never `localStorage`.
- Never roll your own auth or crypto.
- Implement RBAC from day one.

### 1.2 Input Validation

- All input is untrusted. Validate every field at the entry point.
- Use a validation library (Zod, Joi, Pydantic). No manual `if` chains.
- Reject unknown fields explicitly.

### 1.3 Injection Prevention

- No SQL string concatenation — parameterized queries or ORM only.
- Never pass unsanitized input to shell commands, file paths, or `eval`.
- Sanitize all output rendered in a frontend.

### 1.4 Secrets & Configuration

- Zero secrets in code or git — ever.
- All secrets via environment variables or a secrets manager.
- Provide `.env.example` with placeholders. Never commit `.env`.

### 1.5 Data Protection

- Passwords: bcrypt, Argon2, or scrypt only. Never MD5, SHA1, or plain text.
- Sensitive fields encrypted at rest.
- Log the minimum necessary — never log passwords, tokens, or PII.

### 1.6 Transport Security

- HTTPS everywhere.
- Security headers: `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- Rate limiting on all public endpoints; stricter on auth endpoints.

---

## 2. Stability

### 2.1 Error Handling

- No unhandled exceptions. Every async operation wrapped in `try/catch` or a central error handler.
- Never leak stack traces or internal details to the client.
- Standard error response format — use it everywhere:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested item does not exist.",
    "requestId": "abc-123"
  }
}

```

### 2.2 Database Integrity

- Transactions for any multi-table operation.
- Foreign keys enforced at the database level.
- Migrations for all schema changes — never alter production manually. Include a down migration.
- Index every FK and every column in a frequent `WHERE` or `ORDER BY`.
- Never run raw `DELETE` or `UPDATE` without a `WHERE` clause.

### 2.3 Resilience

- Timeouts, retries with exponential backoff, and circuit breakers for all external services.
- Long-running tasks go to a job queue — never block an HTTP request.
- Health check endpoints (`/health`, `/ready`) that verify real dependencies.
- Graceful shutdown: finish in-flight requests, close connections, drain queue before exit.

### 2.4 Idempotency

- All retryable write operations (payments, order creation, emails) must be idempotent.

---

## 3. Code Quality

### 3.1 Structure

- Route → Controller → Service → Repository. Business logic in the service layer only.
- One responsibility per module.
- No magic numbers or magic strings.

### 3.2 TypeScript (if applicable)

- `strict: true`. No `any`. All API shapes typed with shared schema definitions.

### 3.3 Dependencies

- Every dependency must be justified.
- Pin versions. Commit the lockfile.
- Audit regularly. Never use unmaintained packages for critical functions.

### 3.4 Testing

- Every service-layer function has unit tests. Every critical flow has an integration test.
- Tests are isolated — no shared state between tests.
- Mock all external services in tests.
- Failing test blocks deployment.

### 3.5 Logging & Observability

- Structured logging (JSON). Every entry includes: timestamp, severity, request ID, user ID, context.
- Log levels: `DEBUG` / `INFO` / `WARN` / `ERROR` — use them correctly.
- Every production error traceable end-to-end via request ID.

---

## 4. API Design

- REST or GraphQL — consistently, not mixed without documented reason.
- Version all public APIs from day one: `/api/v1/...`
- Correct HTTP status codes — never `200` with `{ "error": true }` in the body.
- Paginate all list endpoints. Default and maximum page size enforced.
- OpenAPI/Swagger documentation generated from code — never written separately.

---

## 5. Deployment

- Application runs identically in local, staging, and production (env vars differ, nothing else).
- No manual production changes. Everything through CI/CD.
- Migrations run automatically before the new version serves traffic.
- Every deployment is rollback-capable within 5 minutes.
- Production never runs in debug mode.

---

## 6. Refactoring Rules

- Never refactor without tests. Write tests first, then refactor.
- Refactor in small, committed steps. One logical change per commit.
- After any refactor, run the full test suite. No disabling tests to make a refactor pass.
- API contract changes require a version bump and migration path.
- Schema changes must be backwards-compatible for at least one release cycle.

---

## 7. Incident & Failure Rules

- Production data exposure, service crash, or data corruption: stop all feature work. Fix first.
- Every production incident gets a post-mortem.
- Alerts must exist for: error rate spikes, response time degradation, disk/memory pressure, failed jobs, failed health checks.
- 80% of incidents diagnosable via logs and dashboards alone — no SSH required.

---

## 8. Non-Negotiable Checklist Before Any Code Is Merged

- [ ] All inputs validated
- [ ] Auth and authorization enforced on new/changed endpoints
- [ ] No secrets in code or logs
- [ ] Error handling complete — no uncaught exceptions possible
- [ ] Parameterized queries or ORM used
- [ ] Transactions wrap multi-step writes
- [ ] Tests written and passing
- [ ] No linter or type errors
- [ ] Migration included for any schema change
- [ ] Logging in place with appropriate level and context
- [ ] No debug code, `console.log` dumps, or TODOs in production paths

---

> **CEO's laatste woord:** Security en stabiliteit zijn geen features. Het zijn het fundament. Wij bouwen systemen die werken — correct, veilig en betrouwbaar — onder alle omstandigheden, altijd. Dit manifest is niet optioneel. Dit is hoe wij overleven.
>
> **Bouw het goed. Bouw het één keer.**
>
> *Vastgesteld door de CEO — Versie 1.1 — 2026 — Alle teams, alle projecten, zonder uitzondering.*

