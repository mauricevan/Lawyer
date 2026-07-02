import { describe, expect, it } from "vitest";
import { FEEDBACK_CATEGORIES } from "./feedbackApi";

describe("FEEDBACK_CATEGORIES", () => {
  it("defines four negative taxonomy labels in Dutch", () => {
    const labels = FEEDBACK_CATEGORIES.map((item) => item.label);
    expect(labels).toEqual(["Onjuist", "Onvolledig", "Bronprobleem", "Gebruiksvriendelijkheid"]);
  });

  it("maps source issues to low ratings", () => {
    const source = FEEDBACK_CATEGORIES.find((item) => item.id === "source_issue");
    expect(source?.rating).toBeLessThanOrEqual(2);
  });
});
