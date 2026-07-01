import { describe, expect, it } from "vitest";
import type { ChatMessage } from "@/models/types";

function applyAssistantResponse(
  messages: ChatMessage[],
  pendingId: string,
  answer: string,
): ChatMessage[] {
  return messages.map((msg) =>
    msg.id === pendingId
      ? { id: pendingId, role: "assistant", content: answer }
      : msg,
  );
}

describe("chat message flow", () => {
  it("adds user and pending assistant optimistically", () => {
    const messages: ChatMessage[] = [];
    const userId = "u1";
    const pendingId = "p1";
    const next = [
      ...messages,
      { id: userId, role: "user" as const, content: "Vraag 1" },
      { id: pendingId, role: "assistant" as const, content: "", isPending: true },
    ];
    expect(next).toHaveLength(2);
    expect(next[1].isPending).toBe(true);
  });

  it("replaces pending message with answer", () => {
    const pendingId = "p1";
    const messages: ChatMessage[] = [
      { id: "u1", role: "user", content: "Vraag" },
      { id: pendingId, role: "assistant", content: "", isPending: true },
    ];
    const result = applyAssistantResponse(messages, pendingId, "Antwoord");
    expect(result[1].content).toBe("Antwoord");
    expect(result[1].isPending).toBeUndefined();
  });
});
