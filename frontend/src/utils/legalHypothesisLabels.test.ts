import { describe, expect, it } from "vitest";
import { parseLegalHypothesis } from "@/utils/legalHypothesisLabels";

describe("parseLegalHypothesis", () => {
  it("parses hypothesis payload from stream detail", () => {
    const parsed = parseLegalHypothesis({
      legal_problem: "Mag een lidstaat e-commerce eisen stellen?",
      legal_actor: "authority",
      legal_domain_guess: "consumer_protection",
      likely_eu_frameworks: ["Directive 2000/31/EC e-commerce"],
      legal_question_type: "national_measure",
    });
    expect(parsed?.legal_domain_guess).toBe("consumer_protection");
    expect(parsed?.likely_eu_frameworks).toHaveLength(1);
  });
});
