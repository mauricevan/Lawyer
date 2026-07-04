# Blueprint: "Uw vraag over EU-regels, helder uitgelegd"
### Technische & functionele specificatie — van A tot Z

---

## Inhoudsopgave

1. [Productvisie & grenzen](#1-productvisie--grenzen)
2. [Architectuuroverzicht](#2-architectuuroverzicht)
3. [Component 1 — Kennisbank (corpus)](#3-component-1--kennisbank-corpus)
4. [Component 2 — EUR-Lex API koppeling](#4-component-2--eur-lex-api-koppeling)
5. [Component 3 — Retrieval systeem (RAG)](#5-component-3--retrieval-systeem-rag)
6. [Component 4 — AI antwoordgenerator](#6-component-4--ai-antwoordgenerator)
7. [Component 5 — Frontend](#7-component-5--frontend)
8. [De volledige vraag-antwoord flow (stap voor stap)](#8-de-volledige-vraag-antwoord-flow-stap-voor-stap)
9. [Voorbeelduitwerking: de douanevraag](#9-voorbeelduitwerking-de-douanevraag)
10. [Technologiekeuzes & stack](#10-technologiekeuzes--stack)
11. [Wat de AI niet mag doen — guardrails](#11-wat-de-ai-niet-mag-doen--guardrails)
12. [Disclaimer & juridische positionering](#12-disclaimer--juridische-positionering)
13. [Implementatieroadmap](#13-implementatieroadmap)
14. [Checklist voor de bouwende AI](#14-checklist-voor-de-bouwende-ai)

---

## 1. Productvisie & grenzen

### Belofte aan de gebruiker
> **"Uw vraag over EU-regels, helder uitgelegd"**

### Wat dit concreet betekent
- De gebruiker stelt een vraag in gewone taal (Nederlands of Engels)
- Het systeem vindt de **exacte, relevante EU-wetgeving** (verordeningen, richtlijnen, artikelen)
- Het systeem geeft een **gestructureerd antwoord** met:
  - Kort antwoord (ja/nee + kern)
  - Relevante artikelen met uitleg
  - Voorwaarden, termijnen, uitzonderingen
  - Directe bronlinks naar EUR-Lex
  - Disclaimer

### Wat het systeem NIET belooft
- Geen persoonlijk juridisch advies
- Geen vervanging van een advocaat
- Geen nationale implementatie (tenzij expliciet uitgebreid)
- Geen garantie op volledigheid bij complexe multidomein-vragen

### Waarom deze grens realistisch én commercieel sterk is
Klanten hebben in 80% van de gevallen alleen nodig:
*"Welk artikel, welke regel, welke termijn?"* — dat levert dit systeem betrouwbaar.
De overige 20% wordt doorverwezen naar een jurist, wat aansprakelijkheidsrisico elimineert.

---

## 2. Architectuuroverzicht

```
┌─────────────────────────────────────────────────────────────┐
│                        GEBRUIKER                            │
│              Stelt vraag in gewone taal (NL/EN)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND (web/app)                         │
│         Invoerveld + antwoordweergave + bronlinks           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               VRAAGVERWERKING (backend)                     │
│  Stap 1: Taaldetectie                                       │
│  Stap 2: Intentie-extractie (domein, kernbegrip, land)      │
│  Stap 3: Query-formulering voor retrieval                   │
└──────┬──────────────────────────────────┬───────────────────┘
       │                                  │
       ▼                                  ▼
┌──────────────────┐            ┌─────────────────────────────┐
│  KENNISBANK      │            │   LIVE EUR-LEX API          │
│  (vector index)  │            │   (SPARQL / REST fallback)  │
│  Vooraf geladen  │            │   Voor recente wijzigingen  │
│  EU-wetgeving    │            │   en ontbrekende documenten │
└──────┬───────────┘            └──────────────┬──────────────┘
       │                                       │
       └──────────────────┬────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              RETRIEVAL (RAG engine)                         │
│  Zoekt meest relevante artikelen + passages                 │
│  Geeft top-5 fragmenten terug met metadata (CELEX, artikel) │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           AI ANTWOORDGENERATOR (LLM)                        │
│  Krijgt: vraag + gevonden wetteksten + instructies          │
│  Produceert: gestructureerd antwoord met bronvermelding     │
│  Mag ALLEEN antwoorden op basis van aangeleverde teksten    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  ANTWOORD AAN GEBRUIKER                     │
│  Kernantwoord | Artikelen | Voorwaarden | Bronlinks         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component 1 — Kennisbank (corpus)

### Het probleem met de huidige software
De software heeft waarschijnlijk **geen of een onvolledige kennisbank**. De AI antwoordt
vanuit zijn trainingsdata — dat is te algemeen, te oud, en niet verifieerbaar met bronlinks.

### Welke EU-documenten moeten in de kennisbank

#### Prioriteit 1 — Kern EU-wetboeken (direct laden)
| Wetgeving | CELEX-nummer | Waarom |
|---|---|---|
| Douanewetboek van de Unie (DWU) | 32013R0952 | Douane, invoer, uitvoer |
| Gedelegeerde Verordening DWU | 32015R2446 | Uitvoeringsregels DWU |
| Uitvoeringsverordening DWU | 32015R2447 | Procedures DWU |
| AVG / GDPR | 32016R0679 | Privacy |
| Productaansprakelijkheidsrichtlijn | 32001L0095 | Productveiligheid |
| AI-verordening | 32024R1689 | AI-wetgeving |
| Richtlijn consumentenrechten | 32011L0083 | E-commerce, B2C |
| Mededingingsverordening | 32022R1925 | DMA |
| Btw-richtlijn | 32006L0112 | Belasting |
| Arbeidstijdenrichtlijn | 32003L0088 | Arbeidsrecht |

#### Prioriteit 2 — Uitbreiden op basis van gebruiksvragen
Analyseer na livegang welke domeinen het meest worden bevraagd en voeg gericht toe.

### Hoe de kennisbank technisch opgebouwd wordt

#### Stap A: Documenten ophalen van EUR-Lex
```
Methode 1 (aanbevolen): EUR-Lex SPARQL endpoint
URL: https://publications.europa.eu/webapi/rdf/sparql

Voorbeeld query — haal alle artikelen op van het DWU:
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?article ?text WHERE {
  ?doc cdm:cellar_id "32013R0952" .
  ?article cdm:part_of ?doc .
  ?article cdm:text ?text .
}

Methode 2 (fallback): REST API
URL: https://eur-lex.europa.eu/legal-content/NL/TXT/HTML/?uri=CELEX:32013R0952
→ Scrapen van HTML, splitsen per artikel
```

#### Stap B: Tekst splitsen in chunks
- Splits per artikel (niet per pagina of willekeurig)
- Elk chunk bevat metadata:
```json
{
  "celex": "32013R0952",
  "wet": "Douanewetboek van de Unie",
  "artikel": "116",
  "lid": "1",
  "titel": "Terugbetaling en kwijtschelding",
  "tekst": "De douaneautoriteiten betalen het bedrag...",
  "url": "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:32013R0952#d1e4521"
}
```

#### Stap C: Embeddings maken
- Genereer voor elk chunk een **vector embedding** (numerieke representatie van de betekenis)
- Sla op in een vector database
- Gebruik: `text-embedding-3-small` (OpenAI) of `multilingual-e5-large` (open source, beter voor NL)

#### Stap D: Vector database
Aanbevolen opties:
- **Supabase** (met pgvector) — eenvoudig, goedkoop, PostgreSQL-gebaseerd
- **Pinecone** — krachtig, managed, iets duurder
- **Weaviate** — open source alternatief

---

## 4. Component 2 — EUR-Lex API koppeling

### Is er een API? Ja, maar met nuances

EUR-Lex heeft meerdere toegangspunten:

#### Optie A: SPARQL endpoint (beste voor gestructureerde queries)
```
Endpoint: https://publications.europa.eu/webapi/rdf/sparql
Formaat: RDF/SPARQL
Voordeel: Officieel, stabiel, gestructureerde metadata
Nadeel: Leercurve, niet alle volledige teksten beschikbaar
```

#### Optie B: EUR-Lex REST/OData API
```
Documentatie: https://eur-lex.europa.eu/content/tools/eur-lex-api/index.html
Toegang: Registratie vereist (gratis)
Endpoint: https://eur-lex.europa.eu/EurLexWebService?wsdl (SOAP)
Modernere REST-variant: in ontwikkeling bij EUR-Lex
Gebruik voor: ophalen van actuele documentversies, recente publicaties
```

#### Optie C: Direct HTML ophalen (eenvoudigste start)
```python
import requests
from bs4 import BeautifulSoup

def haal_eu_wet_op(celex_nummer, taal="NL"):
    url = f"https://eur-lex.europa.eu/legal-content/{taal}/TXT/HTML/?uri=CELEX:{celex_nummer}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Artikelen zitten in <div class="eli-subdivision"> elementen
    artikelen = soup.find_all('div', class_='eli-subdivision')
    return artikelen
```

### Wanneer live API gebruiken vs. kennisbank
| Situatie | Gebruik |
|---|---|
| Standaard vraag over bekende EU-wet | Kennisbank (snel, goedkoop) |
| Vraag over recente verordening (< 6 maanden oud) | Live EUR-Lex API |
| Kennisbank geeft geen resultaat | Fallback naar live API |
| Gebruiker vraagt specifiek om meest recente versie | Live EUR-Lex API |

---

## 5. Component 3 — Retrieval systeem (RAG)

### Wat is RAG en waarom is het cruciaal

RAG = **Retrieval-Augmented Generation**

Zonder RAG: AI beantwoordt op basis van trainingsdata → onbetrouwbaar, geen bronnen
Met RAG: AI zoekt eerst de juiste wettekst op, dan pas antwoord → betrouwbaar, met bronnen

### De retrieval flow in detail

#### Stap 1: Vraaganalyse
```python
# Stuur de vraag eerst naar een LLM voor intentie-extractie
analyse_prompt = """
Analyseer deze juridische vraag en extraheer:
1. Juridisch domein (douane / privacy / consument / arbeid / etc.)
2. Kern rechtsvraag (1 zin)
3. Relevante zoektermen voor EU-wetgeving
4. Land van toepassing (NL/EU-breed)

Vraag: {gebruikersvraag}

Antwoord in JSON:
{
  "domein": "...",
  "rechtsvraag": "...",
  "zoektermen": ["...", "..."],
  "land": "..."
}
"""
```

#### Stap 2: Vector search
```python
def zoek_relevante_artikelen(zoektermen, top_k=8):
    # Maak embedding van de zoekvraag
    query_embedding = maak_embedding(zoektermen)
    
    # Zoek in vector database
    resultaten = vector_db.similarity_search(
        embedding=query_embedding,
        top_k=top_k,
        filter={"domein": gedetecteerd_domein}  # optioneel
    )
    
    return resultaten  # lijst van artikelen + similarity score
```

#### Stap 3: Herranking (reranking)
Niet alle semantisch vergelijkbare teksten zijn even relevant.
Gebruik een reranker om de top-8 te herrangschikken naar top-4 meest relevante artikelen.
```
Aanbevolen: Cohere Rerank API of cross-encoder model
```

#### Stap 4: Context samenstelling
```python
def stel_context_samen(gevonden_artikelen):
    context = ""
    for artikel in gevonden_artikelen[:4]:
        context += f"""
        WET: {artikel['wet']}
        CELEX: {artikel['celex']}
        ARTIKEL: {artikel['artikel']}
        TEKST: {artikel['tekst']}
        URL: {artikel['url']}
        ---
        """
    return context
```

---

## 6. Component 4 — AI antwoordgenerator

### De systeem-prompt (dit is het hart van de software)

Dit is de instructie die de AI bij elke vraag meekrijgt. **Dit is het meest kritieke onderdeel.**

```
SYSTEEM-PROMPT:

Je bent een EU-regelgeving assistent. Jouw taak is EU-regels helder uitleggen
op basis van de aangeleverde wetteksten.

STRIKTE REGELS:
1. Beantwoord UITSLUITEND op basis van de hieronder aangeleverde wetteksten.
2. Als de aangeleverde teksten de vraag niet kunnen beantwoorden, zeg dit
   expliciet: "Op basis van de beschikbare EU-bronnen kan ik dit niet
   beantwoorden. Raadpleeg [specifieke instantie]."
3. Noem ALTIJD het exacte artikel en de verordening/richtlijn.
4. Geef ALTIJD de EUR-Lex URL mee als die beschikbaar is.
5. Gebruik nooit kennis buiten de aangeleverde teksten.
6. Vertaal juridisch taalgebruik naar begrijpelijk Nederlands.
7. Voeg altijd de standaard disclaimer toe aan het einde.

ANTWOORDSTRUCTUUR (verplicht):

## Kort antwoord
[Ja/Nee/Het hangt af van X] — gevolgd door 2-3 zinnen kernantwoord.

## Juridische grondslag
[Welke wet, welk artikel, wat staat er letterlijk]

## Voorwaarden & vereisten
[Genummerde lijst van concrete voorwaarden]

## Termijnen
[Indien van toepassing: concrete termijnen uit de wet]

## Uitzonderingen
[Indien van toepassing]

## Bronnen
- [Naam wet], Art. [X]: [EUR-Lex URL]

## Let op
Dit is juridische informatie, geen persoonlijk juridisch advies. Voor uw
specifieke situatie: raadpleeg een advocaat of [relevante instantie].

---
AANGELEVERDE WETTEKSTEN:
{context}

VRAAG VAN DE GEBRUIKER:
{vraag}
```

### Keuze van het LLM model
| Model | Voor | Tegen | Advies |
|---|---|---|---|
| GPT-4o (OpenAI) | Sterk in redeneren, NL goed | Kosten, data naar VS | Goed voor productie |
| Claude 3.5 Sonnet | Uitstekend in instructies volgen | Kosten | Beste voor nauwkeurigheid |
| Mistral Large | EU-gebaseerd, privacyvriendelijk | Iets minder sterk | Goed als EU-data vereist |
| Llama 3.1 70B | Open source, zelf te hosten | Zelf infrastructuur | Goed voor volledige controle |

**Aanbeveling**: Begin met GPT-4o of Claude — schakel later over naar EU-gehoste optie
als klanten daarom vragen.

### Kritieke instelling: temperature
```
temperature: 0.1  # Zo laag mogelijk — juridische antwoorden moeten consistent zijn
max_tokens: 1500  # Ruim genoeg voor gestructureerd antwoord
```

---

## 7. Component 5 — Frontend

### Minimale vereisten voor een bruikbare interface

#### Invoer
- Groot tekstveld voor de vraag (minstens 4 regels)
- Optioneel: domein-selector (douane / privacy / consument / etc.) voor betere retrieval
- Taalschakelaar NL/EN

#### Antwoordweergave
- Gestructureerd antwoord met kopjes (markdown rendering)
- Bronlinks die direct openen op EUR-Lex
- Kopieerknop voor het antwoord
- "Stel een vervolgvraag" functionaliteit

#### Vertrouwensindicator
Toon bij elk antwoord:
```
Gebaseerd op: Verordening (EU) 952/2013 — Gecontroleerde bron ✓
Artikelen gevonden: 116, 119, 121
Laatste update kennisbank: [datum]
```

#### Escalatiepunt
Bij elke vraag:
```
Heeft u een complexe of specifieke situatie?
→ [Vind een douane-specialist] [Neem contact op]
```

---

## 8. De volledige vraag-antwoord flow (stap voor stap)

```
GEBRUIKER typt:
"Een Nederlandse importeur heeft machines uit Japan ingevoerd. Na de invoer
blijkt dat de douanewaarde te hoog is vastgesteld doordat een korting niet
was verwerkt. Kan de importeur terugbetaling van invoerrechten krijgen?"

    ↓ STAP 1: Taaldetectie
    Taal: Nederlands → antwoord in NL

    ↓ STAP 2: Intentie-extractie (LLM)
    Domein: douane
    Rechtsvraag: terugbetaling invoerrechten bij te hoge douanewaarde
    Zoektermen: ["terugbetaling invoerrechten", "douanewaarde", "correctie",
                 "verzoek terugbetaling douane", "te hoog vastgesteld"]

    ↓ STAP 3: Vector search in kennisbank
    Query: embedding van zoektermen
    Resultaten:
    - DWU Art. 116 (score: 0.94) — terugbetaling invoerrechten
    - DWU Art. 119 (score: 0.89) — terugbetaling bij vergissing
    - DWU Art. 121 (score: 0.86) — termijnen voor verzoek
    - Ged. Reg. Art. 173 (score: 0.81) — procedure correctie douanewaarde

    ↓ STAP 4: Reranking
    Top 4 meest relevante artikelen geselecteerd

    ↓ STAP 5: Context samenstellen
    Volledige artikelteksten + metadata gebundeld

    ↓ STAP 6: LLM genereert antwoord
    Systeem-prompt + context + vraag → gestructureerd antwoord

    ↓ STAP 7: Antwoord terug naar gebruiker
    Met kopjes, bronlinks, disclaimer
```

---

## 9. Voorbeelduitwerking: de douanevraag

Zo zou het antwoord er na implementatie uitzien:

---

### Kort antwoord
**Ja**, een importeur kan terugbetaling van invoerrechten krijgen als de douanewaarde
achteraf te hoog blijkt door een niet-verwerkte korting. Dit valt onder de algemene
terugbetalingsregeling van het Douanewetboek van de Unie.

### Juridische grondslag
**Artikel 116 lid 1 sub a DWU** (Verordening (EU) 952/2013) bepaalt dat
douaneautoriteiten invoerrechten terugbetalen wanneer het bedrag de wettelijk
verschuldigde douaneschuld overschrijdt. Een niet-verwerkte korting op de
transactiewaarde leidt direct tot zo'n onjuiste vaststelling.

### Voorwaarden & vereisten
1. De te veel betaalde rechten moeten aantoonbaar zijn (factuur + kortingsovereenkomst)
2. Schriftelijk verzoek tot terugbetaling indienen bij Douane Nederland
3. Verzoek moet ingediend zijn **binnen 3 jaar** na kennisgeving van de douaneschuld (Art. 121 DWU)
4. De aangever (of vertegenwoordiger) dient het verzoek in
5. Bewijs van werkelijke transactiewaarde overleggen (gecorrigeerde factuur, kortingsbevestiging leverancier)

### Termijnen
- Verzoek indienen: **uiterlijk 3 jaar** na de datum van mededeling van de douaneschuld
- Beslissing door douane: normaal binnen 30 dagen na indiening volledig dossier

### Uitzonderingen
Terugbetaling kan worden geweigerd bij bedragen onder de drempelwaarde (Art. 116 lid 3 DWU)
of als de onjuiste aangifte het gevolg is van fraude of grove nalatigheid (Art. 119 lid 3 DWU).

### Bronnen
- Verordening (EU) 952/2013, Art. 116: https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:32013R0952
- Verordening (EU) 952/2013, Art. 121: https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:32013R0952

### Let op
Dit is juridische informatie op basis van EU-wetgeving, geen persoonlijk juridisch
advies. Voor uw specifieke situatie — met name de precieze berekening en
procedurestappen in Nederland — raadpleeg Douane Nederland of een douane-specialist.

---

## 10. Technologiekeuzes & stack

### Aanbevolen stack (pragmatisch, snel te bouwen)

```
LAAG              TECHNOLOGIE           REDEN
─────────────────────────────────────────────────────────
Frontend          Next.js / React       Snel, modern, markdown-rendering
Backend API       FastAPI (Python)      Eenvoudig, async, AI-libraries
Embeddings        OpenAI Ada-002 of     Meertalig, goed voor juridisch NL
                  multilingual-e5
Vector DB         Supabase + pgvector   Goedkoop, eenvoudig, PostgreSQL
LLM               GPT-4o of Claude      Beste instructie-opvolging
EUR-Lex toegang   HTML scraping         Eenvoudigste start
                  + SPARQL (fase 2)
Hosting           Vercel (frontend)     Snel live
                  + Railway (backend)
```

### Kosteninschatting per maand (kleine schaal, ~500 vragen/dag)
```
OpenAI embeddings:     ~€5
OpenAI GPT-4o:         ~€50-100 (afhankelijk van vraaglengte)
Supabase:              €25 (pro plan)
Hosting:               €20-40
Totaal:                ~€100-170/maand
```

---

## 11. Wat de AI niet mag doen — guardrails

Bouw deze controles in:

### Hard stops (altijd weigeren)
```python
verboden_patronen = [
    "vertel me hoe ik belasting kan ontduiken",
    "hoe omzeil ik douaneheffingen",
    "maak een nep-factuur",
]
```

### Zachte grenzen (doorverwijzen)
- Vragen over specifieke lopende rechtszaken → doorverwijzen
- Vragen die duidelijk nationale wetgeving vereisen → expliciet melden
- Medische, arbeidsrechtelijke of familierechtvragen met hoge persoonlijke impact → escaleren

### Verplichte escalatie-trigger
Als de vraag één van deze elementen bevat, altijd een advocaat aanbevelen:
- Bedragen > €50.000
- Strafrechtelijke dimensie
- Internationale arbitrage
- Bezwaar/beroep al in gang

---

## 12. Disclaimer & juridische positionering

### Verplicht op elke pagina
```
Dit platform biedt juridische informatie over EU-regelgeving, geen juridisch
advies. De informatie is gebaseerd op officiële EU-bronnen (EUR-Lex) maar kan
onvolledig zijn of niet van toepassing op uw specifieke situatie.
[Bedrijfsnaam] is niet aansprakelijk voor beslissingen genomen op basis van
deze informatie. Raadpleeg altijd een gekwalificeerd jurist voor uw specifieke
situatie.
```

### Productpositionering (wat je wél mag zeggen)
✅ "Wij helpen u EU-regels vinden en begrijpen"
✅ "Juridisch onderzoek ondersteund door AI"
✅ "EU-wetgeving helder uitgelegd met bronnen"
✅ "Uw startpunt voor EU-regelgeving"

### Wat u NIET mag zeggen
❌ "Onze AI is uw advocaat"
❌ "Vervang uw juridisch adviseur"
❌ "Gegarandeerd correct juridisch advies"

---

## 13. Implementatieroadmap

### Fase 1 — MVP (4-6 weken)
- [ ] EUR-Lex documenten laden voor 5 kern-domeinen (douane, AVG, consument, btw, arbeid)
- [ ] Vector database opzetten (Supabase)
- [ ] Embeddings genereren voor alle artikelen
- [ ] Basis retrieval pipeline bouwen
- [ ] Systeem-prompt implementeren en testen
- [ ] Eenvoudige frontend met vraag-antwoord interface
- [ ] Bronlinks werkend
- [ ] Disclaimer op alle pagina's

### Fase 2 — Verbetering (6-10 weken na MVP)
- [ ] Reranking toevoegen voor betere relevantie
- [ ] Domein-selector in frontend
- [ ] Meer EU-wetten toevoegen op basis van gebruiksvragen
- [ ] EUR-Lex live API koppeling voor recente documenten
- [ ] Feedbackmechanisme ("Was dit antwoord nuttig?")
- [ ] Antwoordkwaliteit monitoren

### Fase 3 — Uitbreiding
- [ ] Nationale implementatie toevoegen (NL wetgeving)
- [ ] Jurisprudentie HvJ EU toevoegen
- [ ] Escalatiepad naar juristen (partnership)
- [ ] API aanbieden aan B2B klanten

---

## 14. Checklist voor de bouwende AI

Geef deze checklist aan de AI die de software bouwt:

```
VERPLICHTE IMPLEMENTATIE-EISEN:

□ De AI antwoordt NOOIT zonder eerst de kennisbank te raadplegen
□ Elk antwoord bevat minimaal één CELEX-nummer en artikelnummer
□ Elk antwoord bevat minimaal één werkende EUR-Lex URL
□ De systeem-prompt verbiedt antwoorden buiten de aangeleverde context
□ Als geen relevante wet gevonden wordt: expliciete melding + doorverwijzing
□ Temperature is ingesteld op maximaal 0.2
□ Elk antwoord eindigt met de standaard disclaimer
□ Bronnen worden getoond als klikbare links
□ De kennisbank bevat minimaal: DWU (32013R0952) volledig geïndexeerd
□ Chunks zijn gesplitst per artikel (niet per pagina)
□ Metadata per chunk: celex, wet, artikel, lid, tekst, url
□ Retrieval haalt minimaal 5 kandidaat-artikelen op
□ Antwoordstructuur volgt altijd het verplichte format
□ Systeem logt welke artikelen gebruikt zijn per vraag (voor kwaliteitscontrole)

VERBODEN:
□ Antwoorden genereren zonder context uit kennisbank
□ Artikelnummers noemen die niet in de aangeleverde context staan
□ Stellige conclusies trekken over nationale wetgeving
□ De disclaimer weglaten
□ "Ik weet het niet" zonder doorverwijzing naar EUR-Lex of specialist
```

---

*Blueprint versie 1.0 — Op basis van EUR-Lex openbare API en RAG-architectuur*
*Juridische positionering: juridische informatie, geen juridisch advies*
