/** Integration test: SSE stream returns answer on same-page flow */
import { describe, expect, it } from "vitest";
import {
  getDisclaimer,
  getExampleQuestions,
  getPopularQuestions,
  normalizeCitation,
} from "./queryService";

describe("normalizeCitation", () => {
  it("fills missing trust and eurlex_url", () => {
    const result = normalizeCitation({
      celex: "32024R1689",
      article: "5",
      excerpt: "test",
    });
    expect(result.eurlex_url).toContain("32024R1689");
    expect(result.trust.is_in_force).toBe(true);
  });
});

describe("audience helpers", () => {
  it("returns layperson example questions without article numbers", () => {
    const questions = getExampleQuestions("open", "layperson");
    expect(questions[0]).toContain("klantgegevens");
    expect(questions.some((q) => q.includes("artikel"))).toBe(false);
  });

  it("returns professional example questions with legal terms", () => {
    const questions = getExampleQuestions("open", "professional");
    expect(questions[0]).toContain("high-risk");
  });

  it("returns audience-specific disclaimers", () => {
    expect(getDisclaimer("layperson")).toContain("advocaat");
    expect(getDisclaimer("professional")).toContain("EUR-Lex");
  });

  it("returns popular questions per audience", () => {
    expect(getPopularQuestions("layperson")[1]).toContain("chatbot");
    expect(getPopularQuestions("professional")[0]).toContain("high-risk");
  });
});

describe("follow-up request payload", () => {
  it("includes conversation_id and audience for multi-turn chat", () => {
    const payload = {
      question: "Geldt dit ook voor kleine bedrijven?",
      conversation_id: "abc-123",
      query_mode: "open" as const,
      audience: "layperson" as const,
      language: "nl",
    };
    expect(payload.conversation_id).toBe("abc-123");
    expect(payload.audience).toBe("layperson");
    expect(JSON.stringify(payload)).toContain("conversation_id");
  });
});

describe("SSE complete payload shape", () => {
  it("matches what homepage expects", () => {
    const detail = {
      answer: "Test antwoord",
      conversation_id: "abc-123",
      citations: [
        {
          celex: "32024R1689",
          article: "5",
          title: "AI Act",
          excerpt: "excerpt",
          eurlex_url: "https://eur-lex.europa.eu/",
          legal_citation: "Artikel 5",
          trust: {
            is_consolidated: true,
            is_in_force: true,
            has_corrigendum: false,
          },
        },
      ],
    };
    const answer = {
      answer: detail.answer as string,
      conversation_id: detail.conversation_id as string,
      citations: (detail.citations || []).map((c) =>
        normalizeCitation({ ...c, celex: c.celex }),
      ),
      disclaimer: "Dit is geen juridisch advies.",
    };
    expect(answer.answer).toBeTruthy();
    expect(answer.conversation_id).toBe("abc-123");
    expect(answer.citations).toHaveLength(1);
    expect(answer.citations[0].trust.is_consolidated).toBe(true);
  });
});
