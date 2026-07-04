#!/usr/bin/env node
/**
 * Shared strict scoring for layperson clarity audits.
 * Used by layperson-clarity-audit.mjs and layperson-novel-audit.mjs.
 */
export const WEAK = [
  "kan dit niet bevestigen",
  "kan niet bevestigen",
  "geen informatie",
  "geen antwoord",
  "buiten wat ik",
  "artikel none",
  "celex:",
  "skip to main content",
  "lijkt artikel",
  "zijn relevant voor uw vraag",
  "zijn hier relevant",
  "de regels over -",
  "gezien het voorstel van de commissie",
  "having regard to the proposal",
  "| article |",
  "| body",
  ".xml",
];

export function checkSemanticRules(data, rules = {}) {
  const issues = [];
  const answer = (data.answer || "").toLowerCase();
  const mustMention = rules.must_mention || [];
  const mustNot = rules.must_not_contain || [];
  if (mustMention.length && !mustMention.some((term) => answer.includes(term.toLowerCase()))) {
    issues.push(`missing mention: ${mustMention.join("|")}`);
  }
  for (const term of mustNot) {
    if (answer.includes(term.toLowerCase())) issues.push(`forbidden term: ${term}`);
  }
  if (rules.expected_route && data.retrieval_route !== rules.expected_route) {
    issues.push(`route=${data.retrieval_route || "-"}, expected ${rules.expected_route}`);
  }
  return issues;
}

export function scoreAuditCase(testCase, data, scorer) {
  const semanticIssues = checkSemanticRules(data, testCase);
  const clarity = scorer(testCase, data);
  if (semanticIssues.length && clarity === "GOED") return { clarity: "SLECHT", semanticIssues };
  return { clarity, semanticIssues };
}

export function parseAuditArgs(argv) {
  const base = argv[2] && !argv[2].startsWith("--") ? argv[2] : process.env.API_URL || "http://localhost:8003";
  const jsonOut = argv.includes("--json");
  return { base, jsonOut };
}

export function isHeldereUitgelegd(data) {
  const a = data.answer || "";
  const low = a.toLowerCase();
  if (data.coverage_status !== "adequate") return false;
  if (WEAK.some((p) => low.includes(p))) return false;
  if (!a.includes("## Kort antwoord") || !a.includes("## Uitleg")) return false;
  if (/\b320\d{2}[RL]\d{4}\b|CELEX:/i.test(a)) return false;
  if (/lijkt artikel .* relevant/i.test(a)) return false;
  if (/\.xml\b|\| article \||\| body/i.test(a)) return false;
  if ((a.match(/## Kort antwoord/g) || []).length > 1) return false;
  if (/artikel \d+ \| article/i.test(a)) return false;
  if (a.length < 200) return false;
  const kort = (a.split("## Uitleg")[0] || a).slice(0, 400);
  const direct = /\b(ja|nee|wel|niet|is|zijn|kan|kunnen|geldt|gelden|verboden|recht op|mag|moet|minimaal|maximaal|ten minste|meestal|soms|blijft|hebt|heeft|€|\d)/i.test(
    kort,
  );
  return direct;
}
