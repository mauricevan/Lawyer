import type { Audience } from "@/models/types";

export const DISCLAIMER_LAYPERSON =
  "Dit is algemene informatie op basis van EUR-Lex, geen persoonlijk juridisch advies. " +
  "Bij twijfel: raadpleeg een advocaat.";

export const DISCLAIMER_PROFESSIONAL =
  "Dit is geen juridisch advies. Controleer altijd de bron op EUR-Lex en " +
  "verifieer de toepasselijke versie en inwerkingtreding.";

export const ESCALATION_LAYPERSON =
  "Voor bindend advies over uw specifieke situatie kunt u een advocaat of juridisch adviseur raadplegen.";

export const ESCALATION_PROFESSIONAL =
  "Voor dossier-specifieke interpretatie: escaleer naar een gekwalificeerde jurist of compliance officer.";

export function getDisclaimer(audience: Audience = "layperson"): string {
  return audience === "professional" ? DISCLAIMER_PROFESSIONAL : DISCLAIMER_LAYPERSON;
}

export function getEscalationText(audience: Audience = "layperson"): string {
  return audience === "professional" ? ESCALATION_PROFESSIONAL : ESCALATION_LAYPERSON;
}

export const PRODUCT_LIMITATIONS = [
  "Antwoorden zijn gebaseerd op geïndexeerde EUR-Lex/CELLAR-data en kunnen vertraagd zijn.",
  "Live fallback levert mogelijk beperkte of synthetische fragmenten bij trage EUR-Lex-responses.",
  "Geen dekking van nationale implementatiewetgeving tenzij expliciet in bronnen aanwezig.",
  "Historische versies kunnen onvolledig zijn; controleer inwerkingtreding op EUR-Lex.",
] as const;
