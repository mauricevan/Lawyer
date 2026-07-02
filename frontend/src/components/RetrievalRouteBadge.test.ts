import { describe, expect, it } from "vitest";
import { getRouteLabel } from "./RetrievalRouteBadge";

describe("RetrievalRouteBadge labels", () => {
  it("maps all retrieval routes to user-facing labels", () => {
    expect(getRouteLabel("local")).toContain("Lokale");
    expect(getRouteLabel("live_fallback")).toContain("Live");
    expect(getRouteLabel("hybrid")).toContain("Hybride");
    expect(getRouteLabel("cache")).toContain("Cache");
  });
});
