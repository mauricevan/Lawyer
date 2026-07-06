# Plan: Declarant-pijplijn (one-shot)

**Doel:** Het platform werkt zoals een declarant (en een goede AI-assistent) werkt: **denken → zo nodig doorvragen → EUR-Lex → vergelijken → antwoord in lekentaal**.

**Niet doen:** Nog een laag op `agent_v4` + planner + G3 + publish-guard fixes.

**Wel doen:** **Eén nieuwe hoofdroute** voor leekvragen; oude route uit voor dit publiek.

Dit sluit aan op `docs/engineering/production-reasoning-plan-v2.md` — maar dan **één uitvoerbaar pakket**, niet weer 20 incrementele stappen.

**Status:** vastgesteld — bindende productafspraak  
**Versie:** 1.1 — 2026-07-06

---

## 1. Gewenste flow (vast contract)

```
Gebruikersvraag (+ gesprekgeschiedenis)
        ↓
[1] DENKEN (geen EUR-Lex, geen Qdrant)
    - Wat wil de gebruiker weten?
    - Welke wet(en) zijn waarschijnlijk relevant? (mag uit kennis)
    - Wat ontbreek er nog om te kunnen zoeken?
        ↓
[2] KLAAR OM TE ZOEKEN?
    NEE → doorvragen met chips/suggesties → terug naar [1]
    JA  → verder
        ↓
[3] ZOEKEN (gericht, niet “willekeurig chunks”)
    - CELEX + artikelen uit denkstap (mag uit kennis/trainingsdata als hypothese)
    - EUR-Lex: volledig artikel ophalen
    - Optioneel: Qdrant alleen als cache
    - Nog niet genoeg info na fetch? → terug naar [2] (doorvragen), niet gokken
        ↓
[4] VERIFIËREN
    - Past de opgehaalde wettekst bij de casus/vraag?
    NEE → terug naar [1], [2] (meer info), of eerlijk gap met uitleg
    JA  → verder
        ↓
[5] ANTWOORD (lekentaal)
    - Kort antwoord
    - Wat de wet zegt (met verordening + artikelen)
    - Letterlijke EUR-Lex-tekst (inklapbaar)
    - Onzekerheden waar nodig
```

**Kernregel:** De AI mag wet en artikel **voorstellen**, maar **mag niet publiceren** zonder dat de tekst op EUR-Lex is opgehaald en bij de vraag past.

---

## 2. One-shot architectuur

### Nieuw: één orchestrator

`DeclarantPipelineService` — **enige ingang** voor `audience=layperson` (later optioneel expliciet `declarant_mode`).

**State machine met 5 statussen:** `THINK` → `CLARIFY` → `FETCH` → `VERIFY` → `ANSWER` (of `GAP`).

**Dossier** (één object per gesprek, groeit mee):

- `user_goal`, `role`, `facts[]`, `missing_info[]`
- `hypothesis_celex[]`, `hypothesis_articles[]`
- `fetched_chunks[]`, `verification_ok`
- `clarification_round` (max 2)

### Hergebruiken (niet opnieuw uitvinden)


| Bestaand                                              | Rol in nieuwe pijplijn                 |
| ----------------------------------------------------- | -------------------------------------- |
| `legal_case_analysis_service`                         | Denkstap: conflict, domein, CELEX-hint |
| `legal_hypothesis_service`                            | Hypothese wet/artikel                  |
| `clarification_question_service` + chips/formatter    | Doorvragen met suggesties              |
| `effective_question_resolver` + history merge         | Multi-turn                             |
| `eurlex_research_service` + `eurlex_document_session` | Gericht artikel ophalen                |
| `evidence_validation_service`                         | Casus vs wettekst                      |
| `layperson_synoptic_composer` + grounded extractive   | Antwoord vorm                          |
| `explanation_publish_guard`                           | Blijft — krijgt nu correcte input      |
| `citation_builder` + `citation_verifier`              | Bronnen                                |


### Uitschakelen voor leek-route (dag 1: bypass, niet per se verwijderen)


| Oud pad                                                    | Waarom weg                      |
| ---------------------------------------------------------- | ------------------------------- |
| `agent_v4_pipeline` als hoofdroute layperson               | Verkeerde volgorde              |
| Planner-first (`legal_source_planner` als primaire router) | Vervangen door denkstap         |
| Planner-framed templates zonder fetch                      | Gokken zonder verify            |
| G3 hops + branch classifier                                | Extra zoekrondes, instabiliteit |
| `vague_question_service` op agent-pad                      | Blokkeert vóór denken           |
| Doctrine / multi-judge stack                               | Niet in hot path, ruis          |
| LLM-antwoord vóór fetch                                    | Omkeren                         |


### Aanpassen (klein)

- **ILCL:** niet meer “stop en wacht” als standaard — alleen `CLARIFY` met chips; na 2 rondes: **aannames expliciet** + toch zoeken.
- **Publish guard:** `allowed_articles` = opgehaalde artikelen waarvoor chunk-tekst bestaat (hypothese alleen na succesvolle fetch).

---

## 3. Implementatie in één levering

Geschat: **één gerichte sprint**.

### Dag 1–2: Orchestrator + state machine

- `DeclarantPipelineService.run(request, history)`
- Dossier-model (`shared/schemas/declarant_dossier.py`)
- `rag_service` → layperson altijd naar declarant-pijplijn

### Dag 2–3: Denkstap

- LLM + regels: `user_goal`, `missing_info`, `hypothesis_celex/articles`
- Output: `ready_to_search: bool`
- Geen externe calls behalve LLM

### Dag 3–4: Clarify-stap

- Als `not ready_to_search`: 1–3 chips + korte vraag
- `coverage_status: clarify_only` (bestaand UI-patroon)
- Merge chip-antwoord → dossier → opnieuw DENKEN

### Dag 4–5: Fetch-stap (kern)

- Van hypothese: `EurlexResearchService` — **artikel voor artikel**, niet vector-gokken
- Fallback: `eu_legal_research_loop` (1 budget, geen G3)

### Dag 5–6: Verify + Answer

- `evidence_validation_service`: past tekst bij vraag?
- Composer: synoptic + officiële tekst uit chunks
- Publish guard → render

### Dag 6–7: Tests + oude pad uit

- Feature flag `declarant_pipeline_enabled=true` default voor layperson
- Oude layperson-pad achter flag `legacy_layperson=false`

---

## 4. Testplan (slagingscriterium)

### A. Referentie-methode

Per testvraag:

1. **Referentie-antwoord** (menselijk/AI-baseline): kort antwoord + CELEX + artikelen + kernzin uit wet
2. **Platform-antwoord** via API
3. **Score** op:
  - Juiste wet (CELEX)
  - Juiste hoofdartikelen (min. 1 primair)
  - Synoptisch kort antwoord (geen muur tekst)
  - `coverage_status=adequate` OF eerlijke `clarify_only` met zinvolle chips
  - Geen verboden domein (douane bij GDPR-vraag, etc.)
  - Geen artikel genoemd dat niet in opgehaalde tekst staat

### B. Vaste testset (minimum 8)


| #   | Vraag                                                | Referentie kern                              | Verwacht CELEX / art.                 |
| --- | ---------------------------------------------------- | -------------------------------------------- | ------------------------------------- |
| 1   | E-mail werkgever → reclamebedrijf                    | Meestal niet zonder rechtsgrond              | 32016R0679 — 6, 7, 21, 13             |
| 2   | Webshop speelgoed wanneer terugroepen                | Zodra onveilig                               | 32023R0988 — 9, 31, 32                |
| 3   | Online schoenen terugsturen                          | 14 dagen herroeping                          | 32011L0083 — 9                        |
| 4   | Lidstaten douane-unie                                | Lijst in DWU art. 4; beginsel VWEU art. 28   | 32013R0952 art. 4 + 12016E028 art. 28 |
| 5   | Douaneaangifte pakketjes China <150€                 | IOSS/douaneplicht afhankelijk van regime     | 32013R0952 — o.a. 156                 |
| 6   | “Moet ik douaneaangifte doen?” (vaag)                | **Eerst doorvragen** (import EU/derde land?) | `clarify_only`, geen antwoord         |
| 7   | Legitimeren EU overheidsdienst                       | EU-kader + nationaal deel                    | 32004L0038 / 32014R0910               |
| 8   | Mag werkgever GPSR-documenten van leverancier eisen? | Informatieplicht keten                       | 32023R0988 — relevante art.           |


Vragen 4 en 6 zijn de **lakmoest** voor de declarant-workflow.

### C. Automatisering

- Script: `backend/scripts/run_declarant_acceptance.py` (uitbreiden `declarant_catalog` + nieuwe cases)
- CI: deze suite **blokkeert merge** (niet de volledige backend-suite)
- Handmatig: periodiek 2 random vragen naast referentie leggen

### D. Definition of done

- **8/8** adequate of bewuste clarify (vraag 6)
- **0** antwoorden met artikel zonder EUR-Lex-chunk
- **0** “kon niet onderbouwen” bij vragen 1–5 en 7–8
- Blind review: 4 antwoorden naast referentie — “zou ik dit zo aan een collega geven?” → ja

---

## 5. Bewust buiten scope (one-shot)

- Volledige doctrine/multi-judge verwijderen (alleen bypass)
- Nationale wettenbank integratie (wel disclaimer “check nationaal recht”)
- Professional/attorney audience
- Alle 20 declarant-catalog scenarios dag 1 (wel direct daarna)

---

## 6. Risico’s


| Risico                            | Mitigatie                                      |
| --------------------------------- | ---------------------------------------------- |
| Verkeerde wet gekozen in denkstap | Verify-stap + max 1 retry met andere hypothese |
| EUR-Lex traag/kapot               | Timeout + eerlijke melding + link naar EUR-Lex |
| Te veel doorvragen                | Max 2 rondes, daarna aannames + zoeken         |
| Brexit/oude consolidatie DWU      | Actuele versie + waarschuwing waar nodig       |
| LLM 429                           | Denkstap: regel-fallback via case analysis     |


---

## 7. Waarom one-shot (vs. eerdere aanpak)


| Tot nu toe                               | Dit plan                         |
| ---------------------------------------- | -------------------------------- |
| Patches op retrieval-first               | **Nieuwe enige route** layperson |
| Planner als noodplank                    | Planner **uit** hoofdpad         |
| Meerdere systemen die elkaar tegenwerken | **1 state machine**              |
| Tests op lapwerk                         | Tests op **declarant-workflow**  |


---

## 8. Productbeslissing

**Standaard voor alle leekvragen = declarant-pijplijn.**  
Geen aparte modus die standaard uit staat.

---

**Kernregel:** De AI mag wet en artikel **voorstellen** (ook uit trainingsdata of interne kennis), maar **mag niet publiceren** zonder dat de tekst op EUR-Lex is opgehaald en bij de vraag past.

**Doorvragen:** vóór én tijdens het zoeken — tot de vraag/casus bruikbaar is of max. 2 rondes bereikt (daarna expliciete aannames + verder).

---

## 9. Bindende productafspraak (CEO / producteigenaar)

> Deze sectie is de letterlijke vastlegging van de afspraak tussen producteigenaar en engineering.  
> **Geen interpretatieruimte:** implementatie en tests moeten hieraan voldoen. Alleen bij een **technische limiet** (met bewijs) mag hier van worden afgeweken — dan expliciet rapporteren, niet stilzwijgend een andere route bouwen.

### 9.1 Wat de gebruiker vroeg (samenvatting)

1. **Eerst denken** — niet zoeken, redeneren over de vraag.
2. **Check:** genoeg info om te zoeken? Zo nee → **weder vraag** met **gebruiksvriendelijke suggesties** (chips).
3. **Ook tijdens zoeken:** als blijkt dat info ontbreekt → opnieuw doorvragen tot de vraag bruikbaar is.
4. **Hypothese mag uit kennis/trainingsdata/database** — mits **altijd geverifieerd tegen EUR-Lex-wettekst** vóór publicatie.
5. **Zoeken op EUR-Lex** — gericht, niet blind retrieval.
6. **Casus vergelijken met wettekst** — alleen bij match: antwoord in **lekentaal** met **relevante verordening/wet + artikelen**.
7. Geen antwoord publiceren dat niet door de verify-stap komt.

### 9.2 Wat engineering heeft bevestigd

| Vraag | Antwoord |
|-------|----------|
| Snap je het? | **Ja.** |
| Kan het gemaakt worden? | **Ja.** |
| Zie je foutruimte? | **Ja** — verkeerde wet kiezen, EUR-Lex incompleet, te veel/weinig doorvragen, nationaal recht buiten EUR-Lex. **Opvangbaar** via verify-stap en eerlijke gaps. |

### 9.3 Wat engineering **niet** mag doen

- ❌ Retrieval-first of planner-first als hoofdroute layperson
- ❌ Planner-templates publiceren zonder EUR-Lex-verify
- ❌ “Kon niet onderbouwen” terwijl denk → fetch → verify wél had gekund
- ❌ Lapmiddelen per testcase (hardcoded vraag/antwoord)
- ❌ Stilzwijgend afwijken van deze flow zonder technische-limiet-rapportage

### 9.4 Wanneer wél “technische limiet” melden

Alleen als na implementatie van deze pijplijn blijkt dat iets **structureel** niet kan, bijvoorbeeld:

- EUR-Lex levert geen bruikbare tekst (timeout, lege parse) na gerichte fetch
- Vraag valt buiten EU-bronnen (puur nationaal recht)
- Externe API permanent onbereikbaar

Dan: **eerlijke gap** + wat de gebruiker wél kan doen (EUR-Lex-link, herformuleren, jurist) — geen verzonnen antwoord.

### 9.5 Referentie: oorspronkelijke gebruikersvraag (archief)

<details>
<summary>Volledige tekst producteigenaar → Cursor AI (2026-07-06)</summary>

Ok dan moeten we dus weer het platform op de schop gooien — ik dacht dat ik dit al een aantal keer had uitgelegd maar zal het nog een keer uitleggen. Ik wil dat de AI van het platform een vraag krijgt en of snapt dat de vraag niet compleet genoeg is om te zoeken en dus een weder vraag stelt tot dat de vraag compleet is om wel te zoeken. Als deze gaat zoeken en er tijdens het zoeken achter komt dat hij toch niet genoeg informatie heeft, nog meer vragen stellen aan de gebruiker om tot een volledig bruikbare vraag te komen. Hij mag van mij best data halen uit zijn database of trainingsdata als dit beter werkt, als hij het maar verifieert met de wettekst.

Kort: gebruikersvraag → AI denkt eerst (niet zoeken) → genoeg om te zoeken? Zo ja zoeken, zo nee doorvragen met suggesties → EUR-Lex opzoeken → casus tegen wetteksten vergelijken → bij match antwoord in lekentaal met verordening/wet + artikelen.

</details>

---

## Samenvatting

Vervang de layperson-route door één pijplijn: **denken → doorvragen (ook na fetch) → gericht EUR-Lex → verifiëren → lekentaal**. Test met 8 vragen; de douane-unievraag en de vage douaneaangifte-vraag zijn de belangrijkste acceptatietoetsen. **Sectie 9 is bindend.**
