# Gap-analyse EU Q&A Platform

**Datum:** 2026-07-03  
**Baseline:** L 20/20, N 17/18, V 18/18, AQ 15/15, eurlex 10/10, **50 topics**

## Samenvatting

| Type | Aantal (geschat) | Oplossing |
|------|------------------|-----------|
| **A** — Geen topic | ~35% gaps | Fase 2: topics 50→≥80 |
| **B** — Retrieval OK, adequacy faalt | ~15% | Fase 4.2 kalibratie (voorzichtig) |
| **C** — Corpus ontbreekt | ~10% | Fase 4.1 CELEX ingest |

## Type A — Geen topic (prioriteit Fase 2)

| Thema | Voorbeeldvraag | Voorgesteld topic |
|-------|----------------|-------------------|
| Privacy | Spam-sms, GPS-tracker auto | `spam_sms`, `gps_tracking_auto` |
| Consument | Maaltijdbox prijsverhoging, dark patterns | `maaltijdbox_prijsverhoging`, `dark_patterns_webshop` |
| Digitaal | NFT-fraude, AI sollicitatie | `nft_fraude`, `ai_beslissing_sollicitatie` |
| Mobiliteit | Bezorgdrone, CO2 auto, instapweigering | `bezorgdrone_registratie`, `co2_uitstoot_auto_koop`, `vliegtuig_instapweigering` |
| Douane/logistiek | Verloren pakket EU | `grensoverschrijdend_pakket` |
| Arbeid/pensioen | Pensioen buitenland | `pensioen_buitenland` |
| Voedsel | Foodtruck hygiëne | `foodtruck_hygiene` |
| AVG vereniging | Ledenlijst vereniging | `vereniging_ledenlijst_avg` |
| Digitaal inhoud | Gebrekkige download/app | `digitale_inhoud_gebrekkig` |

## Type B — Adequacy faalt (score &lt; 0.35)

| Voorbeeld | Symptoom | Actie |
|-----------|----------|-------|
| Transport aansprakelijkheid | Chunks zwak, gap | Corpus + topic `transport_goederen_aansprakelijkheid` |
| Whistleblower (vóór topic) | insufficient | Opgelost via `eu_whistleblower` |
| Long-tail LLM | Pipe-dump → gap | Hybrid boilerplate pad (P2) |

**Drempel:** 0.35 — niet verlagen zonder L/N/V/W groen.

## Type C — Corpus ontbreekt

| CELEX | Onderwerp | Status |
|-------|-----------|--------|
| 32023R1114 | MiCA / crypto | Toe te voegen |
| 32019L0770 | Digitale inhoud | Toe te voegen |
| 32018R0644 | Pakketbezorging | Toe te voegen |
| 32023R0851 | CO2 auto | Toe te voegen |
| 32004R0852 | Voedselhygiëne | Toe te voegen |
| 32021R2115 | Drones (UAS) | Toe te voegen |

## False positives (Fase 3)

| Topic | Probleem | Fix |
|-------|----------|-----|
| `drone_privacy` | Bezorgdrone/schoolreis matcht privacy-drone | exclude_patterns + min_pattern_hits: 2 |
| `online_warranty` | Restvoorraad-webshop matcht garantie | exclude_patterns + min_pattern_hits: 2 |

## Thematische gaps (Fase 5)

Generieke fallback te vaak — uitbreiden met privacy/consument/arbeid/digitaal thema's in `coverage_guidance.yaml`.

## Meetdoel pilot

≥80% adequate of thematisch nuttige gap; W-set ≥70% GOED na Fase 2–6.
