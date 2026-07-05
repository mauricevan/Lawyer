import type { Audience, ChatMessage } from "@/models/types";

export const CLARIFICATION_INPUT_HINT_ID = "clarification-input-hint";

/** True for ILCL pre-retrieval clarification — not post-answer verification prompts. */
export function isClarificationMessage(message: ChatMessage): boolean {
  return message.coverageStatus === "clarify_only";
}

/** Layperson ILCL only: short answer chips, never full-sentence verification prompts. */
export function isLaypersonClarificationChip(option: string): boolean {
  const text = option.trim();
  if (!text || text.length > 80) return false;
  if (text.includes("?")) return false;
  if (/^(waar|welke|hoe|in welk|wat voor soort|gaat het|kunt u)\b/i.test(text)) return false;
  return text.split(/\s+/).length <= 8;
}

export function filterLaypersonClarificationChips(options: string[]): string[] {
  const seen = new Set<string>();
  return options.filter((option) => {
    const cleaned = option.trim();
    if (!cleaned || seen.has(cleaned) || !isLaypersonClarificationChip(cleaned)) return false;
    seen.add(cleaned);
    return true;
  }).slice(0, 5);
}

/** Layperson ILCL only: short answer chips, never full-sentence verification prompts. */
export function shouldUseClarificationPanel(
  message: ChatMessage,
  audience: Audience = "layperson",
): boolean {
  const chips = message.verificationQuestions ?? [];
  const validChips = audience === "layperson" ? filterLaypersonClarificationChips(chips) : chips;
  return (
    audience === "layperson"
    && message.coverageStatus === "clarify_only"
    && validChips.length > 0
  );
}

/** Id of the latest assistant message that still needs a chip or typed reply. */
export function getActiveClarificationMessageId(
  messages: ChatMessage[],
  audience: Audience = "layperson",
): string | null {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role !== "assistant" || message.isPending) continue;
    if (shouldUseClarificationPanel(message, audience)) return message.id;
    return null;
  }
  return null;
}

/** True while the user must pick a clarification chip before anything else. */
export function hasPendingClarificationInput(
  messages: ChatMessage[],
  audience: Audience,
  isLoading: boolean,
): boolean {
  if (isLoading) return false;
  const activeId = getActiveClarificationMessageId(messages, audience);
  if (!activeId) return false;
  const message = messages.find((item) => item.id === activeId);
  const chips = message?.verificationQuestions ?? [];
  const validChips = audience === "layperson" ? filterLaypersonClarificationChips(chips) : chips;
  return validChips.length > 0;
}
