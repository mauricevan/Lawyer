import type { Audience, SupportedLanguage } from "@/models/types";

type DisclaimerBundle = Record<Audience, string>;
type LanguageCode = Exclude<SupportedLanguage, "auto">;

const DISCLAIMERS: Record<LanguageCode, DisclaimerBundle> = {
  nl: {
    layperson:
      "Dit is algemene informatie op basis van EUR-Lex, geen persoonlijk juridisch advies. " +
      "Bij twijfel: raadpleeg een advocaat.",
    professional:
      "Dit is geen juridisch advies. Controleer altijd de bron op EUR-Lex en " +
      "verifieer de toepasselijke versie en inwerkingtreding.",
  },
  en: {
    layperson:
      "This is general information based on EUR-Lex, not personal legal advice. " +
      "When in doubt, consult a lawyer.",
    professional:
      "This is not legal advice. Always verify the source on EUR-Lex and " +
      "confirm the applicable version and entry into force.",
  },
  fr: {
    layperson:
      "Ceci est une information générale basée sur EUR-Lex, pas un conseil juridique personnel. " +
      "En cas de doute, consultez un avocat.",
    professional:
      "Ceci n'est pas un avis juridique. Vérifiez toujours la source sur EUR-Lex et " +
      "la version applicable ainsi que son entrée en vigueur.",
  },
  de: {
    layperson:
      "Dies sind allgemeine Informationen auf Basis von EUR-Lex, keine persönliche Rechtsberatung. " +
      "Im Zweifel wenden Sie sich an einen Anwalt.",
    professional:
      "Dies ist keine Rechtsberatung. Prüfen Sie stets die Quelle auf EUR-Lex sowie " +
      "die anwendbare Fassung und ihr Inkrafttreten.",
  },
  es: {
    layperson:
      "Esta es información general basada en EUR-Lex, no asesoramiento jurídico personal. " +
      "En caso de duda, consulte a un abogado.",
    professional:
      "Esto no es asesoramiento jurídico. Verifique siempre la fuente en EUR-Lex y " +
      "la versión aplicable y su entrada en vigor.",
  },
};

const ESCALATIONS: Record<LanguageCode, DisclaimerBundle> = {
  nl: {
    layperson:
      "Voor bindend advies over uw specifieke situatie kunt u een advocaat of juridisch adviseur raadplegen.",
    professional:
      "Voor dossier-specifieke interpretatie: escaleer naar een gekwalificeerde jurist of compliance officer.",
  },
  en: {
    layperson: "For binding advice on your situation, consult a qualified lawyer.",
    professional: "For case-specific interpretation, escalate to qualified counsel or compliance.",
  },
  fr: {
    layperson: "Pour un avis contraignant, consultez un avocat qualifié.",
    professional: "Pour une interprétation spécifique au dossier, escaladez vers un juriste qualifié.",
  },
  de: {
    layperson: "Für verbindliche Beratung wenden Sie sich an einen qualifizierten Anwalt.",
    professional: "Für fallbezogene Auslegung eskalieren Sie an qualifizierte Juristen oder Compliance.",
  },
  es: {
    layperson: "Para asesoramiento vinculante, consulte a un abogado cualificado.",
    professional: "Para interpretación específica del caso, escale a un jurista o compliance cualificado.",
  },
};

export const DISCLAIMER_LAYPERSON = DISCLAIMERS.nl.layperson;
export const DISCLAIMER_PROFESSIONAL = DISCLAIMERS.nl.professional;
export const ESCALATION_LAYPERSON = ESCALATIONS.nl.layperson;
export const ESCALATION_PROFESSIONAL = ESCALATIONS.nl.professional;

const PRODUCT_LIMITATIONS_BY_LANG: Record<LanguageCode, readonly string[]> = {
  nl: [
    "Antwoorden zijn gebaseerd op geïndexeerde EUR-Lex/CELLAR-data en kunnen vertraagd zijn.",
    "Live fallback levert mogelijk beperkte of synthetische fragmenten bij trage EUR-Lex-responses.",
    "Geen dekking van nationale implementatiewetgeving tenzij expliciet in bronnen aanwezig.",
    "Historische versies kunnen onvolledig zijn; controleer inwerkingtreding op EUR-Lex.",
  ],
  en: [
    "Answers are based on indexed EUR-Lex/CELLAR data and may be delayed.",
    "Live fallback may return limited fragments when EUR-Lex is slow.",
    "National transposition laws are not covered unless explicitly present in sources.",
    "Historical versions may be incomplete; verify entry into force on EUR-Lex.",
  ],
  fr: [
    "Les réponses reposent sur des données EUR-Lex/CELLAR indexées et peuvent être retardées.",
    "Le repli en direct peut fournir des fragments limités si EUR-Lex est lent.",
    "Pas de couverture des lois nationales de transposition sauf si présentes dans les sources.",
    "Les versions historiques peuvent être incomplètes; vérifiez l'entrée en vigueur sur EUR-Lex.",
  ],
  de: [
    "Antworten basieren auf indexierten EUR-Lex/CELLAR-Daten und können verzögert sein.",
    "Live-Fallback kann begrenzte Fragmente liefern, wenn EUR-Lex langsam ist.",
    "Nationale Umsetzungsgesetze sind nicht abgedeckt, sofern nicht in den Quellen.",
    "Historische Fassungen können unvollständig sein; Inkrafttreten auf EUR-Lex prüfen.",
  ],
  es: [
    "Las respuestas se basan en datos EUR-Lex/CELLAR indexados y pueden retrasarse.",
    "El fallback en vivo puede devolver fragmentos limitados si EUR-Lex es lento.",
    "No cubre leyes nacionales de transposición salvo que figuren en las fuentes.",
    "Las versiones históricas pueden estar incompletas; verifique la entrada en vigor en EUR-Lex.",
  ],
};

/** Dutch default for static pages (juridische-informatie). */
export const PRODUCT_LIMITATIONS = PRODUCT_LIMITATIONS_BY_LANG.nl;

function resolveLanguage(language: SupportedLanguage = "nl"): LanguageCode {
  return language === "auto" ? "nl" : language;
}

export function getProductLimitations(language: SupportedLanguage = "nl"): readonly string[] {
  return PRODUCT_LIMITATIONS_BY_LANG[resolveLanguage(language)];
}

export function getDisclaimer(
  audience: Audience = "layperson",
  language: SupportedLanguage = "nl",
): string {
  const lang = resolveLanguage(language);
  return DISCLAIMERS[lang][audience];
}

export function getEscalationText(
  audience: Audience = "layperson",
  language: SupportedLanguage = "nl",
): string {
  const lang = resolveLanguage(language);
  return ESCALATIONS[lang][audience];
}
