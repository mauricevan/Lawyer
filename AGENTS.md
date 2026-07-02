# AI AGENT CODE MANIFEST

### *Niet onderhandelen. Dit is hoe wij bouwen.*

**Versie 1.0 — Vastgesteld door de CEO**

---

## 0. MINDSET — Begrijp dit of begin er niet aan

Elke regel code die jij schrijft representeert dit bedrijf.  
Slechte code kost geld. Technische schuld doodt bedrijven.  
Jij bent geen typemachine — jij bent een engineer met verantwoordelijkheid.  
**Denk eerst. Schrijf daarna.**  

**Let op voor elke nieuwe taak die je gaat uivoeren zorg en bepaal dat er genoeg context grote over is anders run eerst een context compact**

**indien een taak gedaan is en goed met bewijs gestest is, maak een commit naar github.**

---

## 1. BESTANDSSTRUCTUUR & GROOTTE

- **Maximaal 250 regels per bestand.** Geen uitzonderingen.
- Splitst een bestand op als het richting 200 regels gaat — wacht niet op 250.
- Eén bestand = één verantwoordelijkheid *(Single Responsibility Principle)*.
- Gebruik altijd een **logische mappenstructuur** voor je begint:

```
/src
  /components      ← UI-bouwstenen
  /services        ← business logica & API-calls
  /utils           ← herbruikbare hulpfuncties
  /models          ← datastructuren & types
  /tests           ← alle testbestanden
/docs              ← documentatie
/config            ← omgevingsinstellingen
```

- Geen "rommelbestanden" zoals `helpers2.js`, `final_v3_echt_nu.py`. **Nooit.**

---

## 2. CODE HERGEBRUIK — DRY IS WET GELD

> *"Don't Repeat Yourself" is geen suggestie. Het is financieel beleid.*

- Schrijf je iets voor de **tweede keer**? Stop. Maak een functie.
- Schrijf je iets voor de **derde keer**? Stop. Maak een module.
- Controleer altijd **eerst** of er al een utility/service/component bestaat voordat je iets nieuws schrijft.
- Deel gedeelde logica op in `/utils` of `/services` — **nooit inline herhalen**.
- Gebruik bestaande **libraries** voor standaardproblemen (datums, validatie, HTTP). Het wiel wordt niet opnieuw uitgevonden in dit bedrijf.

---

## 3. NAAMGEVING — Als je het niet kunt uitleggen, geef het een andere naam

- Variabelen, functies en klassen krijgen **beschrijvende namen** in het Engels.
- Geen: `x`, `data2`, `tmpResult`, `doStuff()`, `handleThings()`
- Wel: `calculateMonthlyRevenue()`, `userAuthToken`, `parseInvoiceItems()`
- **Boolean variabelen** starten altijd met `is`, `has`, of `can`: `isLoading`, `hasPermission`
- **Functies** zijn werkwoorden: `fetchUser()`, `validateEmail()`, `renderDashboard()`
- **Klassen/Components** zijn zelfstandige naamwoorden: `UserService`, `InvoiceModel`
- Consistentie per taal: camelCase (JS/TS), snake_case (Python), PascalCase (classes overal)

---

## 4. FUNCTIES — Klein, scherp, één doel

- Een functie doet **één ding**. Als je "en" gebruikt om het te beschrijven, splits dan.
- Maximaal **20 regels** per functie. Meer = heroverweeg de opzet.
- Maximaal **3 parameters**. Meer nodig? Gebruik een object/struct.
- **Pure functies** verdienen de voorkeur: zelfde input → zelfde output, geen verborgen bijwerkingen.
- Functies die kunnen falen retourneren **expliciete errors**, gooien ze niet stilletjes weg.

---

## 5. HIËRARCHIE & ARCHITECTUUR

Elke codebase volgt **3 lagen**. Niet meer, niet minder:

```
┌─────────────────────────────┐
│  PRESENTATIE (UI / Output)  │  ← Wat de gebruiker ziet
├─────────────────────────────┤
│  LOGICA (Services / Rules)  │  ← Wat het systeem doet
├─────────────────────────────┤
│  DATA (Models / Storage)    │  ← Wat het systeem onthoudt
└─────────────────────────────┘
```

**Lagen spreken alleen met hun directe buur.** UI roept nooit direct de database aan.  
Schending van dit principe = onmiddellijk refactoren voordat verder wordt gegaan.

---

## 6. CODE REVIEW — Vier ogen zien meer dan twee

Elke substantiële wijziging doorloopt deze checklist **voordat** het gecommit wordt:

### ✅ Zelf-review (verplicht, altijd)

- [ ] Voldoet de code aan de 250-regel limiet per bestand?
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

> *Geen test = geen productie. Dit is geen beleid, dit is zelfrespect.*

### Teststrategie (verplicht):

- **Unit tests** voor elke utility-functie en service-methode
- **Integratietests** voor elke API-endpoint en datasource-connectie
- **Edge case tests**: lege input, null-waarden, extreme getallen, verkeerde datatypes

### Minimale testdekking:


| Laag              | Minimaal |
| ----------------- | -------- |
| Utils / Helpers   | **90%**  |
| Services / Logica | **80%**  |
| API Endpoints     | **75%**  |
| UI Components     | **60%**  |


### Testregel:

- Testbestand staat altijd naast of in `/tests` met dezelfde naam + `.test` of `_test`
- Tests draaien **lokaal groen** voordat iets gecommit wordt
- Een falende test is een **stopbord**, geen gele kaart

---

## 8. FOUTAFHANDELING — Plan voor het ergste, bouw voor het beste

- Elke externe call (API, database, bestandssysteem) krijgt **expliciete foutafhandeling**
- Foutmeldingen zijn **menselijk leesbaar** én **debugbaar** (log de context, niet alleen "Error occurred")
- Gebruik **geen** lege catch-blokken: `catch(e) {}` is een misdaad
- Onderscheid **verwachte fouten** (gebruikersinvoer) van **onverwachte fouten** (systeemstoringen)
- Kritieke fouten worden **gelogd met timestamp, context en stack trace**

---

## 9. DOCUMENTATIE — Code vertelt wat. Documentatie vertelt waarom.

- Elk bestand begint met een **korte header**: wat doet dit, wie is de eigenaar, wanneer aangemaakt.
- Elke publieke functie krijgt een **docstring/JSDoc** met: doel, parameters, return-waarde.
- Complexe logica krijgt een **inline comment** boven de betreffende regels.
- Een `README.md` per module die uitlegt: doel, hoe te gebruiken, dependencies.
- **Nooit** verouderde comments laten staan. Stale comments zijn erger dan geen comments.

---

## 10. SECURITY — Vertrouw niemand, ook niet jezelf

- **Nooit** API-keys, wachtwoorden of tokens in code of git. Altijd `.env` + `.gitignore`.
- **Valideer altijd** alle input van buiten — gebruiker, API, bestand, alles.
- **Principle of Least Privilege**: een module krijgt alleen toegang tot wat hij écht nodig heeft.
- Gebruikersdata wordt **nooit gelogd** in plain text.
- Dependencies worden **wekelijks gescand** op bekende kwetsbaarheden (`npm audit`, `pip-audit`).

---

## 11. PERFORMANCE — Snel is een feature

- Optimaliseer **nooit prematuur** — bouw eerst correct, meet dan, optimaliseer daarna.
- Grote datasets worden **gepagineerd of gestreamd** — nooit in één keer in geheugen geladen.
- Database-queries krijgen altijd een **index-analyse** bij meer dan 1.000 records.
- Frontend-componenten worden **alleen gerenderd als hun data verandert**.
- Zware operaties draaien **asynchroon** — de gebruiker wacht nooit zonder feedback.

---

## 12. GIT DISCIPLINE — Geschiedenis is documentatie

- **Commitberichten** zijn beschrijvend: `feat: add invoice pagination`, `fix: null check in user auth`
- Gebruik het **Conventional Commits** formaat: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Eén commit = één logische wijziging. Geen "WIP dump"-commits naar main.
- **Feature branches** altijd. Nooit rechtstreeks op `main` of `develop` pushen.
- Branch-naamgeving: `feature/`, `fix/`, `refactor/`, `docs/`

---

## 13. AGENT-SPECIFIEKE REGELS — Jij bent AI. Gedraag je ernaar.

> *Deze sectie is speciaal voor jou, agent. Lees hem dubbel.*

- **Vraag bij twijfel.** Aannames zijn de moeder van alle bugs. Als de opdracht niet 100% helder is, vraag dan om verduidelijking vóór je begint.
- **Werk incrementeel.** Lever kleine, werkende stukken op. Geen monolithische dumps van 500 regels.
- **Verwijder nooit bestaande code** zonder het expliciet te vermelden en te motiveren.
- **Geen magic numbers.** `const MAX_RETRIES = 3` niet `if (retries > 3)`.
- **Controleer altijd** of de code die je schrijft past in het bestaande architectuurpatroon.
- **Test je eigen output.** Schrijf de test, draai hem mentaal door, lever dan de code.
- Als iets niet kan worden opgelost binnen de regels van dit manifest — **meld het**, los het niet stilletjes op op een slechte manier.
- **Refactor als je slechte code ziet**, ook als het niet de opdracht was. We laten geen puinhoop achter.

---

## 14. DEFINITIE VAN "KLAAR"

Een taak is **pas klaar** als:

- [ ] Code voldoet aan alle regels van dit manifest
- [ ] Alle relevante tests zijn geschreven én groen
- [ ] Geen linter-fouten of -waarschuwingen
- [ ] Code is self-review'd via checklist in sectie 6
- [ ] Documentatie is bijgewerkt
- [ ] Commit staat op de juiste branch met correct bericht

**Niet klaar = niet klaar. Er is geen "95% klaar".**

---

## ⚡ CEO'S LAATSTE WOORD

Wij bouwen software die over 5 jaar nog onderhoudbaar is.  
Niet software die vandaag werkt en morgen iemand anders problem is.  

Elk compromis op kwaliteit is een factuur die later betaald wordt — met rente.  
Dit manifest is niet optioneel. Dit is hoe wij overleven.

**Bouw het goed. Bouw het één keer.**

---

*Vastgesteld door de CEO — Bijgewerkt: 2026 — Alle teams, alle projecten, zonder uitzondering.*

# FRONTEND DESIGN SPECIFICATIE

## Het Handvest van de Drie Disciplines

> Dit document is het fundament. Geen regel code wordt geschreven voordat elk onderdeel hiervan is doorgelezen, begrepen en geaccordeerd. Het is opgesteld vanuit drie perspectieven: **gedragspsychologie**, **visueel ontwerp**, en **frontend engineering**.

---

## DEEL 1 — GEDRAGSPSYCHOLOGIE

*Hoe mensen zien, lezen, voelen en beslissen*

### 1.1 Cognitieve belasting (Cognitive Load)

- Het werkgeheugen van een gebruiker kan maximaal **5–9 elementen** tegelijk verwerken (Miller's Law). Beperk de zichtbare keuzes per schermgebied strikt.
- Gebruik **chunking**: groepeer gerelateerde informatie visueel zodat de hersenen patronen herkennen in plaats van losse items te scannen.
- Vermijd **informatiedichtheid**: een scherm vol tekst, icoontjes en CTA-knoppen veroorzaakt keuzeverlamming. Elke pagina heeft **één primair doel**.
- Gebruik de **Hick-Hyman Law**: hoe meer keuzes, hoe langer de beslissingstijd. Minimaliseer navigatie-opties, formuliervelden en menu-items.

### 1.2 Visuele aandacht en scangedrag

- Gebruikers lezen niet — ze **scannen** in een F-patroon (desktop) of lineair van boven naar beneden (mobiel).
- Plaats de meest kritische informatie in de **bovenste 200px** van het scherm (above the fold).
- Gebruik **witruimte actief**: een leeg vlak trekt de blik naar het naastgelegen element. Witruimte is geen verspilling, het is richting.
- **Contrast** bepaalt wat gezien wordt. Het wichtigste element op de pagina heeft het hoogste contrast met zijn achtergrond.
- Gebruik **grootte-hiërarchie**: de grootste tekst/het grootste element krijgt als eerste aandacht. Zorg dat dit ook het meest relevante element is.

### 1.3 Vertrouwen en geloofwaardigheid

- Consistentie bouwt vertrouwen. Elementen die er hetzelfde uitzien, gedragen zich ook hetzelfde — altijd.
- **Micro-interacties** (subtiele hover-states, laad-animaties, bevestigingen) geven de gebruiker het gevoel dat het systeem reageert en leeft.
- Vermijd **dark patterns**: misleidende ontwerpen die de gebruiker manipuleren (verborgen opt-outs, urgentiefraude, misleidende knoppen). Dit vernietigt vertrouwen permanent.
- Feedback moet **onmiddellijk** zijn. Als een actie langer dan 200ms duurt, geef een visuele bevestiging (spinner, progress, skelet-scherm).

### 1.4 Emotie en kleur (psychologische werking)


| Kleur     | Psychologische associatie         | Gebruik                              |
| --------- | --------------------------------- | ------------------------------------ |
| Blauw     | Vertrouwen, rust, betrouwbaarheid | Banken, SaaS, gezondheidszorg        |
| Groen     | Groei, veiligheid, succes         | Bevestigingen, duurzaamheid, finance |
| Rood      | Urgentie, gevaar, energie         | Foutmeldingen, uitverkoop-CTA's      |
| Oranje    | Vriendelijkheid, actie, warmte    | CTA-knoppen, jonge doelgroepen       |
| Paars     | Luxe, creativiteit, mysterie      | Premium producten, mode              |
| Zwart     | Autoriteit, elegantie, luxe       | High-end merken                      |
| Wit/Grijs | Neutraliteit, ruimte, helderheid  | Achtergronden, adempauzes            |


- **Kleur is nooit de enige informatiedrager.** Kleurblinde gebruikers (~8% mannen) mogen geen informatie missen. Combineer altijd kleur met vorm, tekst of icoon.
- Gebruik **maximaal 3 kleuren** in de primaire UI (primair, accent, neutraal). Statuskleuren (succes, fout, waarschuwing, info) zijn aanvullend.

### 1.5 Toegankelijkheid als ethische plicht

- Toegankelijkheid is geen feature — het is het **minimum**. Ontwerp voor mensen met visuele, motorische, cognitieve en auditieve beperkingen.
- Houd de **WCAG 2.1 AA** standaard aan als absoluut minimum; streef naar AAA waar mogelijk.
- Ontwerp voor **toetsenbordnavigatie**: elke interactieve functie moet bereikbaar zijn zonder muis.
- Zorg voor **focus-states** die altijd zichtbaar zijn — verwijder nooit `outline` zonder een gelijkwaardig alternatief.

---

## DEEL 2 — VISUEEL ONTWERP

*De taal van het oog*

### 2.1 Kleurensysteem

```
KLEURARCHITECTUUR (definieer vóór aanvang):

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

**Regels:**

- Geen hardcoded hexwaarden in componenten — altijd CSS custom properties.
- Lichte modus EN donkere modus worden tegelijkertijd ontworpen, nooit achteraf.
- Contrastverhouding tekst op achtergrond: minimaal **4.5:1** (normaal), **3:1** (grote tekst ≥18px bold of ≥24px).

### 2.2 Typografie

```
TYPE SCHAAL (modular scale, voorkeur ratio 1.25 of 1.333):

--font-display:   [karaktervol display-font, spaarzaam]
--font-body:      [leesbaar body-font, ≥16px basis]
--font-mono:      [monospace voor code/data]

--text-xs:   0.75rem   (12px)
--text-sm:   0.875rem  (14px)
--text-base: 1rem      (16px)   ← minimale bodytekst
--text-md:   1.125rem  (18px)
--text-lg:   1.25rem   (20px)
--text-xl:   1.5rem    (24px)
--text-2xl:  1.875rem  (30px)
--text-3xl:  2.25rem   (36px)
--text-4xl:  3rem      (48px)
--text-5xl:  3.75rem   (60px)
```

**Regels:**

- **Nooit** minder dan `16px` voor bodytekst — op geen enkel apparaat.
- Regellengte (line-length) maximaal **65–75 tekens** per regel voor optimale leesbaarheid.
- Regelafstand (line-height): `1.5` voor body, `1.2` voor koppen.
- Letter-spacing: koppen licht negatief (`-0.01em` tot `-0.03em`), uppercase labels licht positief (`0.05em`).
- Maximaal **2 lettertypefamilies** per project. Meer dan 2 is chaos.
- Gebruik **font-display: swap** bij webfonts — nooit een FOIT (Flash of Invisible Text).

### 2.3 Spatiëring en grid

```
SPATIE SCHAAL (basis 4px):

--space-1:   4px
--space-2:   8px
--space-3:   12px
--space-4:   16px
--space-5:   20px
--space-6:   24px
--space-8:   32px
--space-10:  40px
--space-12:  48px
--space-16:  64px
--space-20:  80px
--space-24:  96px
```

**Grid:**

- Desktop: **12-kolommen grid**, 24px gutter, max-breedte `1280px` of `1440px`, gecentreerd.
- Tablet: **8 kolommen**, 20px gutter.
- Mobiel: **4 kolommen**, 16px gutter, 16px marge links/rechts.
- Gebruik **CSS Grid** voor paginalayout, **Flexbox** voor componentinterne lay-out.

### 2.4 Componenten — visuele standaarden

#### Knoppen

```
Primaire knop:    hoge contrast, merkkleur, duidelijke hover/active-state
Secundaire knop:  outline of ghost, subtiel
Tertiaire knop:   tekst-only, minimalistische actie
Destructieve knop: rood, altijd met bevestigingsdialoog

Minimale klikoppervlak: 44×44px (Apple HIG / WCAG 2.5.5)
Border-radius: consistent in het hele systeem (kies: 0 / 4px / 8px / 12px / pill)
```

#### Formuliervelden

```
Hoogte: minimaal 44px op mobiel, 40px op desktop
Label: altijd zichtbaar BOVEN het veld, nooit alleen placeholder
Placeholder: enkel als voorbeeld-inhoud, verdwijnt bij typen
Foutmelding: direct onder het veld, rood + icoon + beschrijvende tekst
Focus-state: duidelijke outline (minimaal 2px, 3:1 contrast)
Disabled-state: verminderd contrast, geen pointer-events
```

#### Kaarten (cards)

```
Consistente padding: --space-6 of --space-8
Border-radius: zelfde als rest van systeem
Schaduw: licht en subtiel (niet meerdere lagen stapelen)
Hover-state indien klikbaar: subtiele elevatie of kleurverschuiving
```

### 2.5 Iconen

- Gebruik één iconensysteem — niet mengen (bijv. niet half Heroicons, half FontAwesome).
- Minimale icoongrootte: **24×24px** voor interactieve elementen.
- Iconen nooit alleen als informatie — combineer altijd met label of tooltip voor toegankelijkheid.
- Consistent lijndikte (stroke-width) door het hele systeem.

### 2.6 Afbeeldingen en media

- Altijd `aspect-ratio` definiëren om layout shift (CLS) te voorkomen.
- `object-fit: cover` op container-elementen zodat afbeeldingen nooit vervormen.
- `loading="lazy"` op alle afbeeldingen buiten de viewport.
- Decoratieve afbeeldingen: `alt=""` (leeg). Informatieve afbeeldingen: beschrijvende `alt`-tekst.

---

## DEEL 3 — FRONTEND ENGINEERING

*Wat de browser ziet en hoe het presteert*

### 3.1 Responsive design — de absolute regels

**Breakpoints (mobile-first):**

```css
/* Default: mobiel (320px–767px) */

@media (min-width: 768px)  { /* tablet */ }
@media (min-width: 1024px) { /* laptop */ }
@media (min-width: 1280px) { /* desktop */ }
@media (min-width: 1536px) { /* wide desktop */ }
```

**Verboden gedrag:**

- ❌ Vaste `px`-breedtes op containers zonder `max-width`
- ❌ Horizontale scroll op enig schermformaat
- ❌ Tekstafbreuk (`word-break`) tenzij technisch onvermijdelijk
- ❌ Overflow die buiten de viewport steekt
- ❌ Knoppen/links die te klein zijn om op te tikken op mobiel
- ❌ Hover-only functionaliteit (touchscreens kennen geen hover)

**Verplicht gedrag:**

- ✅ `box-sizing: border-box` globaal
- ✅ Alle tekstgroottes in `rem` (relatief aan root), nooit in `px`
- ✅ Alle spatiëring flexibel via `clamp()` of procentuele waarden
- ✅ Afbeeldingen: altijd `max-width: 100%`
- ✅ Testen op minimaal 320px breedte (kleinste gangbare telefoon)

### 3.2 Flexibele typografie met clamp()

```css
/* Schaal vloeiend mee zonder harde breakpoints */
h1 { font-size: clamp(1.75rem, 4vw + 1rem, 3.5rem); }
h2 { font-size: clamp(1.375rem, 3vw + 0.75rem, 2.5rem); }
body { font-size: clamp(1rem, 1.5vw + 0.5rem, 1.125rem); }
```

### 3.3 Layout — geen overflow, geen afbreuk

```css
/* Globale reset die overflow voorkomt */
*, *::before, *::after {
  box-sizing: border-box;
}

html, body {
  overflow-x: hidden;
  max-width: 100%;
}

img, video, canvas, svg {
  max-width: 100%;
  display: block;
}

/* Tekst die niet mag afbreken */
.no-break {
  white-space: nowrap;         /* nooit wrappen */
  overflow: hidden;
  text-overflow: ellipsis;     /* afkappen met ... */
}

/* Tekst die wél mag wrappen maar niet überlopen */
p, li, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;   /* breek woorden alleen als echt nodig */
  hyphens: auto;               /* automatische woordafbreking */
}
```

### 3.4 Performance — Core Web Vitals als design-eis


| Metric                                        | Doel           | Wat het meet                    |
| --------------------------------------------- | -------------- | ------------------------------- |
| **LCP** (Largest Contentful Paint)            | < 2.5 seconden | Laadsnelheid grootste element   |
| **FID** / **INP** (Interaction to Next Paint) | < 200ms        | Reactietijd op interactie       |
| **CLS** (Cumulative Layout Shift)             | < 0.1          | Onverwachte layout-verschuiving |
| **TTFB** (Time to First Byte)                 | < 800ms        | Serverreactietijd               |
| **FCP** (First Contentful Paint)              | < 1.8 seconden | Eerste zichtbare content        |


**Performance-regels:**

- Geen ongeoptimaliseerde afbeeldingen. Gebruik WebP of AVIF als standaard.
- Fonts: maximaal 2 varianten laden (bijv. Regular + Bold). Geen volledige font-families preloaden.
- Critical CSS inline in `<head>`. Niet-kritieke CSS asynchroon laden.
- JavaScript dat de render blokkeert: verboden. Gebruik `defer` of `async`.
- Gebruik `will-change` spaarzaam — alleen bij complexe animaties op GPU-accelerated elementen.

### 3.5 CSS-architectuur

```
BESTANDSSTRUCTUUR:
/styles
  ├── tokens.css          ← alle design tokens (kleuren, fonts, spacing)
  ├── reset.css           ← browser-normalisatie
  ├── typography.css      ← type-scale en headings
  ├── layout.css          ← grid, container, spacing utilities
  ├── components/
  │   ├── button.css
  │   ├── form.css
  │   ├── card.css
  │   └── navigation.css
  ├── pages/              ← pagina-specifieke overschrijvingen
  └── utilities.css       ← kleine helper-classes
```

**Specificiteitsregels:**

- Gebruik **BEM-naamgeving** of een gelijkwaardig systeem — geen kale elementselectors in componenten.
- Nooit `!important` gebruiken, tenzij in utility-classes die bedoeld zijn om alles te overschrijven.
- CSS custom properties zijn de enige bron van waarheid voor kleuren, fonts en spacing.

### 3.6 Animatie en beweging

```css
/* Respekteer gebruik voorkeur — geen beweging als gebruiker dat aangeeft */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Animatieprincipes:**

- Duur: **150–300ms** voor micro-interacties, **300–500ms** voor grotere overgangen.
- Easing: nooit lineair. Gebruik `ease-out` voor elementen die verschijnen, `ease-in` voor elementen die verdwijnen.
- Geen animatie puur voor decoratie — elke beweging communiceert iets (richting, hiërarchie, feedback).
- GPU-animaties uitsluitend via `transform` en `opacity` — nooit via `left/top/width/height`.

### 3.7 HTML-semantiek

- Gebruik de **juiste HTML-elementen** voor hun semantische betekenis:
  - `<nav>` voor navigatie
  - `<main>` voor hoofdinhoud (één per pagina)
  - `<article>`, `<section>`, `<aside>` voor structuur
  - `<button>` voor acties, `<a>` voor navigatie — nooit omgedraaid
  - Koopstructuur: `<h1>` (één per pagina) → `<h2>` → `<h3>` — nooit stappen overslaan
- Alle formuliervelden hebben een gekoppeld `<label>` via `for`/`id`.
- ARIA-attributen alleen als het HTML-equivalent niet beschikbaar is.

### 3.8 Donkere modus

```css
/* Automatisch via systeem-instelling */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f0f;
    --color-surface: #1a1a1a;
    --color-text-primary: #f5f5f5;
    /* ... alle tokens opnieuw definiëren */
  }
}

/* Manuele toggle via data-attribuut */
[data-theme="dark"] {
  --color-bg: #0f0f0f;
  /* ... */
}
```

**Donkere modus-regels:**

- Gebruik geen puur zwart (`#000000`) als achtergrond — gebruik een donker grijs (`#0f0f0f` tot `#1a1a1a`).
- Verlaag de helderheid van afbeeldingen en illustraties in donkere modus (`filter: brightness(0.85)`).
- Schaduwen werken niet op donkere achtergronden — vervang door subtiele borders of glow-effecten.

---

## DEEL 4 — NAVIGATIE EN GEBRUIKERSSTROOM

### 4.1 Navigatieprincipes

- Navigatie is altijd zichtbaar of bereikbaar in **maximaal 1 stap**.
- Actieve pagina is **altijd visueel gemarkeerd** in de navigatie.
- Maximaal **7 items** in de hoofdnavigatie (Miller's Law).
- Mobiele navigatie: hamburger-menu is acceptabel, maar een **bottom navigation bar** heeft de voorkeur bij ≤5 items (vingers reiken naar de onderkant van het scherm).
- Breadcrumbs bij hiërarchieën dieper dan 2 niveaus.

### 4.2 Scrollgedrag

```css
/* Vloeiend scrollen voor in-page links */
html { scroll-behavior: smooth; }

/* Sticky navigatie — voorzichtig: kost schermruimte op mobiel */
nav {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px); /* elegant glas-effect */
}

/* Scroll-marge voor ankerlinks achter sticky nav */
[id] { scroll-margin-top: 80px; }
```

### 4.3 Toetsenbord- en focusbeheer

```css
/* Zichtbare focus — verwijder NOOIT zonder alternatief */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Skip-link voor toetsenbordgebruikers */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
}
.skip-link:focus {
  top: 0;
}
```

---

## DEEL 5 — FORMULIEREN EN FEEDBACK

### 5.1 Formulierontwerp

- Één kolom op mobiel — altijd.
- Volgorde van velden: logisch en chronologisch (naam → email → bericht, niet willekeurig).
- Verplichte velden: markeer verplicht met `*` EN een legenda "* = verplicht". Markeer optionele velden met "(optioneel)" in het label.
- Geen captcha tenzij strikt noodzakelijk. Gebruik honeypot-velden als alternatief.
- Bewaar formulierstatus bij fout — leeg een formulier nooit volledig bij een fout.

### 5.2 Foutafhandeling

```
FOUTMELDING-PATROON:
1. Rood border op het veld
2. Rood icoon (⚠ of ✕) naast het label
3. Beschrijvende foutmelding onder het veld
4. Tekst: "Vul een geldig e-mailadres in (bijv. naam@domein.nl)"
   — niet: "Ongeldig e-mailadres"
5. Foutmelding verschijnt bij blur (verlaten van het veld), niet tijdens typen
6. Bij formulierverzending: focus automatisch naar het eerste veld met een fout
```

### 5.3 Laadstaten en feedback

```
ELKE actie heeft vier staten:
  1. Idle    — standaardstaat, wacht op input
  2. Loading — visuele indicator (spinner, skeleton, progress)
  3. Success — bevestiging (groen, vinkje, bericht)
  4. Error   — foutbericht met hersteloptie

Laadtijddrempels:
  < 100ms  → geen indicator nodig (voelt instant)
  100–300ms → subtiele spinner
  300ms–1s  → prominente spinner
  > 1 seconde → progress bar of skelet-scherm
  > 10 seconden → annuleringsoptie aanbieden
```

---

## DEEL 6 — TESTPROTOCOL

*Controleer vóór elke release*

### 6.1 Apparaattesten

```
VERPLICHTE TESTMATRIX:

Mobiel:
  ☐ iPhone SE (375px)       — kleinste gangbare scherm
  ☐ iPhone 14/15 (390px)    — meest gebruikte iOS
  ☐ Samsung Galaxy S (360px) — meest gebruikte Android
  ☐ Staand EN liggend

Tablet:
  ☐ iPad (768px)
  ☐ iPad Pro (1024px)
  ☐ Staand EN liggend

Desktop:
  ☐ 1280px
  ☐ 1440px
  ☐ 1920px (wide)
  ☐ 2560px (ultra-wide — controleer max-width)

Minimale test: 320px breedte — GEEN horizontale scroll toegestaan
```

### 6.2 Browser-compatibiliteit

```
MINIMALE ONDERSTEUNING:
  ☐ Chrome (laatste 2 versies)
  ☐ Firefox (laatste 2 versies)
  ☐ Safari (laatste 2 versies) — let op: Safari loopt vaak achter
  ☐ Edge (laatste 2 versies)
  ☐ iOS Safari (laatste 2 versies) — test altijd op echt apparaat
  ☐ Samsung Internet (laatste versie)
```

### 6.3 Toegankelijkheidstest

```
AUTOMATISCH:
  ☐ Axe DevTools (of gelijkwaardig)
  ☐ Lighthouse Accessibility score ≥ 90

HANDMATIG:
  ☐ Volledige toetsenbordnavigatie doorlopen
  ☐ Schermlezer-test (NVDA + Firefox / VoiceOver + Safari)
  ☐ Ingezoomd op 200% — geen overflow, geen afgeknipte tekst
  ☐ Kleurenblindsimulatie (bijv. Colorblindly Chrome-extensie)
  ☐ High contrast modus (Windows)
```

### 6.4 Performance-test

```
  ☐ Lighthouse Performance score ≥ 90 (mobiel)
  ☐ LCP < 2.5 seconden
  ☐ CLS < 0.1
  ☐ INP < 200ms
  ☐ Geen afbeeldingen > 200KB zonder expliciete rechtvaardiging
  ☐ Geen renderblocking scripts
```

### 6.5 Inhoudsintegriteitstest

```
  ☐ Geen tekst die buiten zijn container valt
  ☐ Geen afgeknipte afbeeldingen (tenzij bewust ontworpen)
  ☐ Lange woorden/URL's breken correct af (bijv. in foutmeldingen)
  ☐ Lege staten zijn ontworpen (geen data? Wat ziet de gebruiker?)
  ☐ Foutpagina's zijn ontworpen (404, 500)
  ☐ Formuliervalidatie werkt in alle browsers
  ☐ Alle links werken en gaan naar de juiste bestemming
```

---

## DEEL 7 — DESIGN TOKENS TEMPLATE

> Kopieer dit als startpunt voor elk project. Vul in vóór aanvang.

```css
:root {
  /* === KLEUREN === */
  --color-primary:           #000000; /* INVULLEN */
  --color-primary-hover:     #000000;
  --color-primary-active:    #000000;
  --color-primary-subtle:    #000000;

  --color-accent:            #000000;
  --color-accent-hover:      #000000;

  --color-bg:                #ffffff;
  --color-surface:           #f8f8f8;
  --color-surface-hover:     #f0f0f0;
  --color-border:            #e5e5e5;
  --color-border-strong:     #cccccc;

  --color-text-primary:      #111111;
  --color-text-secondary:    #555555;
  --color-text-tertiary:     #888888;
  --color-text-disabled:     #aaaaaa;
  --color-text-inverse:      #ffffff;

  --color-success:           #16a34a;
  --color-success-bg:        #f0fdf4;
  --color-warning:           #d97706;
  --color-warning-bg:        #fffbeb;
  --color-error:             #dc2626;
  --color-error-bg:          #fef2f2;
  --color-info:              #2563eb;
  --color-info-bg:           #eff6ff;

  /* === TYPOGRAFIE === */
  --font-display:  'INVULLEN', sans-serif;
  --font-body:     'INVULLEN', sans-serif;
  --font-mono:     'INVULLEN', monospace;

  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-md:   1.125rem;
  --text-lg:   1.25rem;
  --text-xl:   1.5rem;
  --text-2xl:  1.875rem;
  --text-3xl:  2.25rem;
  --text-4xl:  3rem;
  --text-5xl:  3.75rem;

  --leading-tight:  1.2;
  --leading-normal: 1.5;
  --leading-loose:  1.75;

  /* === SPATIËRING === */
  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-5:  1.25rem;
  --space-6:  1.5rem;
  --space-8:  2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;

  /* === LAYOUT === */
  --container-sm:  640px;
  --container-md:  768px;
  --container-lg:  1024px;
  --container-xl:  1280px;
  --container-2xl: 1536px;

  /* === RADIUS === */
  --radius-sm:   4px;   /* KIES ÉÉN systeem, consistent toepassen */
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-xl:   16px;
  --radius-full: 9999px;

  /* === SCHADUWEN === */
  --shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
  --shadow-md:  0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg:  0 10px 15px rgba(0,0,0,0.1);
  --shadow-xl:  0 20px 25px rgba(0,0,0,0.1);

  /* === ANIMATIE === */
  --duration-fast:   150ms;
  --duration-normal: 250ms;
  --duration-slow:   400ms;
  --ease-out:  cubic-bezier(0, 0, 0.2, 1);
  --ease-in:   cubic-bezier(0.4, 0, 1, 1);
  --ease-inout: cubic-bezier(0.4, 0, 0.2, 1);

  /* === Z-INDEX LAGENMODEL === */
  --z-base:     0;
  --z-dropdown: 100;
  --z-sticky:   200;
  --z-overlay:  300;
  --z-modal:    400;
  --z-toast:    500;
  --z-tooltip:  600;
}
```

---

## GOEDKEURINGSLIJST — VOOR AANVANG

Elke verantwoordelijke parafeert onderstaande lijst voordat de eerste regel code wordt geschreven:

```
DESIGN TOKENS
  ☐ Kleurpalet volledig gedefinieerd en goedgekeurd
  ☐ Typografie-pairing geselecteerd en gelicentieerd
  ☐ Spatiëringssysteem vastgesteld
  ☐ Border-radius keuze bepaald (één waarde voor het hele systeem)
  ☐ Animatieduur en easing vastgesteld

GEDRAG & UX
  ☐ Doelgroep gedefinieerd (leeftijd, apparaatvoorkeur, digitale vaardigheid)
  ☐ Primaire actie per pagina vastgesteld
  ☐ Lege staten ontworpen
  ☐ Foutpagina's ontworpen (404, 500)
  ☐ Laadstaten ontworpen

TECHNISCH
  ☐ Breakpoints vastgesteld en gedocumenteerd
  ☐ CSS-architectuur afgesproken
  ☐ Donkere modus: wel of niet? (beslissing documenteren)
  ☐ Browser-support matrix afgesproken
  ☐ Performance-doelen vastgesteld

TOEGANKELIJKHEID
  ☐ WCAG 2.1 AA geaccepteerd als minimum
  ☐ Toetsenbordnavigatie ingepland in componentontwerp
  ☐ Focus-states ontworpen
  ☐ Alt-tekst-strategie voor afbeeldingen afgesproken
```

---

*Dit document is een levend document. Elke afwijking hiervan vereist expliciete groepsgoedkeuring en wordt gedocumenteerd als uitzondering met reden.*

**Versie:** 1.0  
**Opgesteld door:** Gedragspsychologie × Visueel Ontwerp × Frontend Engineering  
**Status:** Template — invullen per project

# Backend AI Agent — Engineering Standards & Non-Negotiable Rules

> Issued by the CEO. These rules are absolute. No exceptions. No shortcuts. No "I'll fix it later."
> Every AI agent working on this backend must read, understand, and comply with every rule in this document — before writing a single line of code. Violations are not tolerated.

---

## 0. Mindset: You Are Building a Production System

You are not building a prototype. You are not writing demo code. Every decision you make must assume:

- **Real users depend on this system.**
- **Attackers are actively trying to break it.**
- **The codebase will be refactored, extended, and maintained by others.**
- **Downtime costs money and destroys trust.**

If you are ever unsure whether something is "good enough," it isn't. Ask, or choose the safer, more defensive option.

---

## 1. Security — Absolute Rules

### 1.1 Authentication & Authorization

- Every API endpoint must be protected by authentication **by default.** Unauthenticated endpoints are an explicit, documented exception — never the default.
- Authorization checks must happen **inside the service/controller layer**, not just at the gateway. Never assume the caller is trusted.
- Use short-lived tokens (JWT or equivalent). Refresh tokens must be stored securely (HttpOnly cookies or equivalent — never in localStorage).
- Never roll your own authentication or cryptography. Use established, maintained libraries only.
- Implement **role-based access control (RBAC)** from day one, even if there is currently only one role.

### 1.2 Input Validation

- **All input is untrusted.** Validate every field — type, length, format, range — at the entry point (controller/handler layer), before any business logic or database interaction.
- Use a validation library (Zod, Joi, Pydantic, etc.). Never write manual `if` chains for validation.
- Reject unknown fields. Do not silently ignore extra data — strip it explicitly or throw an error.
- Never trust data that comes from the client, even if it came from your own frontend.

### 1.3 Injection Prevention

- Never construct SQL queries with string concatenation. Use **parameterized queries or an ORM exclusively.**
- Never pass unsanitized user input to a shell command, file path, or eval-equivalent function.
- Sanitize all output that will be rendered in a frontend to prevent XSS.

### 1.4 Secrets & Configuration

- **Zero secrets in code.** No API keys, passwords, tokens, or credentials in source files, comments, or commit history — ever.
- All secrets are loaded from environment variables or a secrets manager (e.g. Vault, AWS Secrets Manager, Doppler).
- Provide a `.env.example` file with placeholder values and documentation. Never commit `.env`.
- Rotate secrets if there is any suspicion of exposure. Document the rotation procedure.

### 1.5 Data Protection

- Passwords are always hashed using bcrypt, Argon2, or scrypt. Never MD5, never SHA1, never plain text.
- Sensitive fields (PII, financial data) must be encrypted at rest.
- Log the minimum necessary. **Never log passwords, tokens, full credit card numbers, or PII.**
- Implement data retention policies — don't keep data longer than needed.

### 1.6 Transport Security

- HTTPS everywhere. HTTP is not acceptable in any environment that handles real data.
- Set security headers: `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- Apply rate limiting to all public endpoints. Implement stricter limits on authentication endpoints to prevent brute-force attacks.

---

## 2. Stability — The System Must Never Fall Over

### 2.1 Error Handling

- **No unhandled exceptions.** Every async operation is wrapped in try/catch or uses a central error handler. Unhandled promise rejections crash Node processes — this is unacceptable in production.
- All errors are caught, logged with context, and returned as a structured error response. Never leak stack traces or internal error details to the client.
- Distinguish between **operational errors** (bad input, resource not found — return to client gracefully) and **programmer errors** (bugs — log with full context, alert, and fail safely).
- Define a standard error response format and use it everywhere:
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

- Use **transactions** for any operation that touches more than one table or requires atomicity. A crash mid-operation must never leave the database in a corrupt state.
- Every foreign key relationship must be enforced at the database level — not just in application code.
- Write **database migrations** for all schema changes. Never alter a production schema manually. Migrations must be reversible (include a `down` migration).
- Index every foreign key and every column that appears in a `WHERE` clause or `ORDER BY` in a frequent query. Missing indexes cause slow queries that cascade into outages.
- Never run raw `DELETE` or `UPDATE` without a `WHERE` clause. Add a safeguard or linter rule that prevents this.

### 2.3 Resilience & Graceful Degradation

- Assume external services (payment providers, email, third-party APIs) **will fail**. Implement timeouts, retries with exponential backoff, and circuit breakers.
- Long-running or heavy tasks must be offloaded to a **job queue** (e.g. BullMQ, Celery, SQS). Never block an HTTP request with work that takes more than a few hundred milliseconds.
- Implement health check endpoints (`/health`, `/ready`) that verify database connectivity and critical dependencies — not just that the process is running.
- Design for **graceful shutdown**: on `SIGTERM`, finish in-flight requests, close database connections cleanly, and drain the job queue before exiting.

### 2.4 Idempotency

- All write operations that may be retried (payments, order creation, emails) must be **idempotent**. Use idempotency keys or check-before-write patterns.
- API endpoints that trigger side effects must be safe to call multiple times without duplicating the effect.

---

## 3. Code Quality — Refactor-Safe, Maintainable, Predictable

### 3.1 Structure & Architecture

- Follow a clear, consistent layered architecture: **Routes → Controllers → Services → Repositories/Data Access.** Business logic lives in the service layer only. Never put business logic in a controller or database query.
- One responsibility per module. A file that does authentication and sends emails and calculates prices is a liability.
- Keep functions short and focused. If a function requires more than one scroll to read, it needs to be split.
- **No magic numbers or magic strings.** All constants are named and centralized.

### 3.2 TypeScript / Type Safety (if applicable)

- **Strict mode is on.** `strict: true` in `tsconfig.json`. No exceptions.
- No `any`. If you don't know the type, use `unknown` and narrow it explicitly.
- All API request and response shapes are typed with shared schema definitions. No implicit `object` types crossing API boundaries.

### 3.3 Dependencies

- Every dependency must be justified. Adding a 2MB library to parse a date is not acceptable.
- Pin dependency versions in production. Use a lockfile (`package-lock.json`, `yarn.lock`, `poetry.lock`) and commit it.
- Audit dependencies regularly for known vulnerabilities (`npm audit`, `pip audit`, Dependabot, Snyk).
- Never use a package with zero maintenance, zero tests, or owned by a single unknown person for a critical function.

### 3.4 Testing

- **No untested code in production.** Every service-layer function must have unit tests. Every critical user flow must have an integration test.
- Tests must be isolated — no test depends on the state left by another test.
- Mock external services in tests. Tests must not call real payment APIs, real email servers, or real third-party services.
- A failing test **blocks deployment.** The CI pipeline does not merge or deploy red builds.
- Aim for high coverage on business logic. Coverage alone is not the goal — meaningful assertions are.

### 3.5 Logging & Observability

- Use structured logging (JSON output). Every log entry includes: timestamp, severity level, request ID, user ID (if available), and the relevant context.
- Log at the right level: `DEBUG` for development noise, `INFO` for normal operations, `WARN` for unexpected but recoverable situations, `ERROR` for failures that need attention.
- Instrument key operations: request duration, database query times, queue depths, error rates. These are your early warning system.
- Every production error must be traceable end-to-end using a request ID that flows from the frontend through every service.

---

## 4. API Design — Predictable, Versioned, Documented

- Follow REST conventions consistently, or use GraphQL consistently. Do not mix paradigms without a deliberate, documented reason.
- Version all public APIs from day one: `/api/v1/...`. Changing an unversioned API breaks clients — this is a production incident.
- Return the correct HTTP status codes. `200` for success, `201` for creation, `400` for bad input, `401` for unauthenticated, `403` for unauthorized, `404` for not found, `409` for conflicts, `422` for validation errors, `500` for server errors. Do not return `200` with `{ "error": true }` in the body.
- Paginate all list endpoints. No endpoint returns unbounded lists. Default page size must be defined; maximum page size must be enforced.
- Document every endpoint. Use OpenAPI/Swagger. The documentation is generated from the code — it is never written separately and allowed to drift.

---

## 5. Deployment & Environment Rules

- The application runs identically in local development, staging, and production — the only differences are environment variables.
- **No manual changes to production.** Everything goes through CI/CD. If something was changed by hand, it does not exist.
- Database migrations run automatically as part of the deployment pipeline, before the new application version starts serving traffic.
- Every deployment must be **rollback-capable.** If a deployment causes an incident, the previous version must be restorable within 5 minutes.
- Production never runs in debug mode. Debug logging, detailed error responses, and development tooling are disabled in production.
- Secrets are never passed as command-line arguments (they appear in process lists). Use environment variables or mounted secret files.

---

## 6. Refactoring Rules — Stability Must Survive Change

> Refactoring is not an excuse to break things. The system must be equally stable before and after.

- **Never refactor without tests.** If the code you are changing is untested, write tests first — then refactor.
- Refactor in small, committed steps. One logical change per commit. Do not combine a refactor with a feature change in the same commit.
- After any refactor, run the full test suite. If any test fails, fix it before continuing. Do not disable or delete tests to make a refactor pass.
- If a refactor changes an API contract, it requires a version bump and a migration path for existing consumers.
- Database schema changes during a refactor must be **backwards-compatible** for at least one release cycle to allow safe rollback. Add new columns as nullable; remove old columns only after the code no longer references them.

---

## 7. Incident & Failure Rules

- If a bug reaches production that exposes user data, crashes the service, or causes data corruption: **stop all feature work immediately.** Fix the incident first.
- Every production incident gets a **post-mortem**: what happened, why it happened, what was the impact, and what specific changes prevent recurrence.
- Alerts must exist for: error rate spikes, response time degradation, disk/memory pressure, failed jobs, and failed health checks.
- The on-call engineer must be able to diagnose and resolve 80% of incidents using logs and dashboards alone — without SSH access to the production server.

---

## 8. Non-Negotiable Checklist Before Any Code Is Merged

Before submitting or merging any backend change, the agent must confirm:

- [ ] All inputs are validated
- [ ] Authentication and authorization are enforced on new/changed endpoints
- [ ] No secrets in code or logs
- [ ] Error handling is complete — no uncaught exceptions possible
- [ ] Database operations use parameterized queries or ORM
- [ ] Transactions wrap multi-step writes
- [ ] Tests are written and passing
- [ ] No linter errors or type errors
- [ ] Migration is included for any schema change
- [ ] Logging is in place with appropriate level and context
- [ ] No debug code, `console.log` dumps, or TODOs left in production paths

---

> **Final word from the CEO:**
> Security and stability are not features. They are the foundation. A backend that is fast but insecure is a liability. A backend that is feature-rich but unstable is a liability. We build systems that work — correctly, safely, and reliably — under all conditions, at all times. That is the standard. Hold it.

