import type { LegalHypothesis } from "@/models/types";

const EFFECT_LABELS: Record<string, string> = {
  market_access_prohibition: "Markttoegang verbod",
  discrimination_by_establishment: "Ongelijke behandeling vestiging",
  additional_requirement: "Aanvullende nationale eis",
  licensing_or_authorisation: "Vergunning / toestemming",
  procedural_burden: "Procedurele last",
  enforcement_measure: "Handhaving / toezicht",
};

const CONCLUSION_LABELS: Record<string, string> = {
  permitted: "Toegestaan",
  prohibited: "Niet toegestaan",
  conditional: "Onder voorwaarden",
};

const CONFLICT_LABELS: Record<string, string> = {
  internal_market_restriction: "Beperking interne markt",
  consumer_transaction_issue: "Consumententransactie",
  employment_relationship_issue: "Arbeidsrelatie",
  data_processing_issue: "Gegevensverwerking",
  product_compliance_issue: "Productconformiteit",
  administrative_enforcement_issue: "Handhaving / toezicht",
  platform_governance_issue: "Platformgovernance (DSA)",
};

const RECONCILIATION_LABELS: Record<string, string> = {
  supported: "Ondersteund door bronnen",
  partially_supported: "Gedeeltelijk ondersteund",
  contradicted: "Niet ondersteund door bronnen",
};

const DOMAIN_LABELS: Record<string, string> = {
  consumer_protection: "Consumentenrecht",
  employment_law: "Arbeidsrecht",
  internal_market: "Interne markt",
  administrative_law: "Handhaving / toezicht",
  product_safety: "Productveiligheid",
  data_protection: "Gegevensbescherming (AVG)",
  digital_services: "Digitale diensten (DSA)",
  unknown: "Nog te bepalen",
};

const ACTOR_LABELS: Record<string, string> = {
  manufacturer: "Fabrikant",
  consumer: "Consument",
  employee: "Werknemer",
  authority: "Toezichthouder / lidstaat",
  platform: "Platform",
  operator: "Exploitant",
  unknown: "Niet gespecificeerd",
};

const QUESTION_TYPE_LABELS: Record<string, string> = {
  market_access: "Markttoegang",
  rights: "Rechten",
  obligations: "Verplichtingen",
  enforcement: "Handhaving",
  national_measure: "Nationale maatregel",
  definition: "Definitie / uitleg",
  unknown: "Algemeen",
};

export function labelLegalDomain(domain: string): string {
  return DOMAIN_LABELS[domain] || domain.replaceAll("_", " ");
}

export function labelLegalActor(actor: string): string {
  return ACTOR_LABELS[actor] || actor;
}

export function labelQuestionType(questionType: string): string {
  return QUESTION_TYPE_LABELS[questionType] || questionType.replaceAll("_", " ");
}

export function labelPrimaryConflict(conflict: string): string {
  return CONFLICT_LABELS[conflict] || conflict.replaceAll("_", " ");
}

export function labelReconciliation(conclusion: string): string {
  return RECONCILIATION_LABELS[conclusion] || conclusion.replaceAll("_", " ");
}

export function labelLegalEffect(effectType: string): string {
  return EFFECT_LABELS[effectType] || effectType.replaceAll("_", " ");
}

export function labelEffectConclusion(conclusion: string): string {
  return CONCLUSION_LABELS[conclusion] || conclusion.replaceAll("_", " ");
}

export function parseLegalHypothesis(raw: unknown): LegalHypothesis | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const item = raw as Record<string, unknown>;
  const problem = String(item.legal_problem || "").trim();
  if (!problem) return undefined;
  const frameworks = Array.isArray(item.likely_eu_frameworks)
    ? item.likely_eu_frameworks.map((entry) => String(entry)).filter(Boolean)
    : Array.isArray(item.likely_EU_frameworks)
      ? item.likely_EU_frameworks.map((entry) => String(entry)).filter(Boolean)
      : [];
  return {
    legal_problem: problem,
    legal_actor: String(item.legal_actor || "unknown"),
    legal_domain_guess: String(item.legal_domain_guess || "unknown"),
    likely_eu_frameworks: frameworks,
    legal_question_type: String(item.legal_question_type || "unknown"),
    evidence_valid: typeof item.evidence_valid === "boolean" ? item.evidence_valid : undefined,
    case_summary: item.case_summary ? String(item.case_summary) : undefined,
    context: item.context ? String(item.context) : undefined,
    parties: Array.isArray(item.parties)
      ? item.parties.map((entry) => String(entry)).filter(Boolean)
      : undefined,
    possible_domains: Array.isArray(item.possible_domains)
      ? item.possible_domains.map((entry) => String(entry)).filter(Boolean)
      : undefined,
    primary_legal_conflict: item.primary_legal_conflict
      ? String(item.primary_legal_conflict)
      : undefined,
    legal_effect_type: item.legal_effect_type ? String(item.legal_effect_type) : undefined,
    restriction_strength: item.restriction_strength ? String(item.restriction_strength) : undefined,
    state_action: item.state_action ? String(item.state_action) : undefined,
    effect_conclusion_hint: item.effect_conclusion_hint
      ? String(item.effect_conclusion_hint)
      : undefined,
    reconciliation_conclusion: item.reconciliation_conclusion
      ? String(item.reconciliation_conclusion)
      : undefined,
  };
}
