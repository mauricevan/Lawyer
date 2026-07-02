# Taal-fallback matrix

| Stap | nl | fr | de | es |
|---|---|---|---|---|
| User/API taal | nl | fr | de | es |
| FTS config | dutch | french | german | spanish |
| SPARQL expression | NLD | FRA | DEU | SPA |
| EUR-Lex fetch (1e) | /nl/ | /fr/ | /de/ | /es/ |
| EUR-Lex fallback | en | en | en | en |
| Live discovery | nl→en | fr→en | de→en | es→en |
| Disclaimer | NL | FR | DE | ES |

## `auto`-modus

1. Stopwoord-detectie op vraag
2. Resolve naar enabled taal
3. Retrieval + disclaimer in resolved taal

## Bekende beperkingen

- Geïndexeerde corpus is primair Nederlands; FR/DE/ES lean op multilingual embeddings + live fallback
- Juridische-informatiepagina blijft NL; disclaimers in chat zijn gelokaliseerd
- Antwoordtekst volgt LLM-prompt (NL default); taal van vraag wordt meegenomen in retrieval
