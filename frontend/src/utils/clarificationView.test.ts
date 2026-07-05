import { describe, expect, it } from "vitest";
import { isClarificationMessage, shouldUseClarificationPanel } from "./clarificationView";
import type { ChatMessage } from "@/models/types";

const baseMessage: ChatMessage = {
  id: "1",
  role: "assistant",
  content: "Intro",
};

describe("clarificationView", () => {
  it("detects only ILCL clarify_only messages", () => {
    expect(
      isClarificationMessage({
        ...baseMessage,
        verificationQuestions: ["marktplaats"],
        coverageStatus: "clarify_only",
      }),
    ).toBe(true);
    expect(
      isClarificationMessage({
        ...baseMessage,
        verificationQuestions: ["In welk land woont of werkt u?"],
        coverageStatus: "insufficient",
      }),
    ).toBe(false);
  });

  it("uses clarification panel only for layperson ILCL chips", () => {
    const ilclMessage = {
      ...baseMessage,
      verificationQuestions: ["marktplaats"],
      coverageStatus: "clarify_only" as const,
    };
    expect(shouldUseClarificationPanel(ilclMessage, "layperson")).toBe(true);
    expect(shouldUseClarificationPanel(ilclMessage, "professional")).toBe(false);
  });

  it("rejects question-form verification prompts even on clarify_only", () => {
    const badChipsMessage = {
      ...baseMessage,
      verificationQuestions: ["Waar gaat uw vraag precies over (bijv. privacy, AI, arbeid)?"],
      coverageStatus: "clarify_only" as const,
    };
    expect(shouldUseClarificationPanel(badChipsMessage, "layperson")).toBe(false);
  });
});
