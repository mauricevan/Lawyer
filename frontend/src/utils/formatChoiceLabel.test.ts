import { describe, expect, it } from "vitest";
import { formatChoiceLabel } from "./formatChoiceLabel";

describe("formatChoiceLabel", () => {
  it("title-cases simple chip labels", () => {
    expect(formatChoiceLabel("marktplaats")).toBe("Marktplaats");
    expect(formatChoiceLabel("app / SaaS")).toBe("App / SaaS");
  });
});
