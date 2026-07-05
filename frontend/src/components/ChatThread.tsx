"use client";

import { useEffect, useRef } from "react";
import { ClarificationPanel } from "./ClarificationPanel";
import { LegalHypothesisPanel } from "./LegalHypothesisPanel";
import { LaypersonMarkdown } from "./LaypersonMarkdown";
import type { Audience, ChatMessage } from "@/models/types";
import {
  filterLaypersonClarificationChips,
  getActiveClarificationMessageId,
  shouldUseClarificationPanel,
} from "@/utils/clarificationView";
import { scrollIntoViewRespectingMotion } from "@/utils/scrollIntoViewRespectingMotion";
import { AnswerProvenance } from "./AnswerProvenance";
import { CitationSources } from "./CitationSources";
import { CoverageGuidancePanel } from "./CoverageGuidancePanel";
import { FeedbackPanel } from "./FeedbackPanel";
import { VerificationQuestions } from "./VerificationQuestions";
import chatLayoutStyles from "./ChatLayout.module.css";
import styles from "./ChatThread.module.css";

interface Props {
  messages: ChatMessage[];
  audience?: Audience;
  conversationId?: string;
  onVerificationSelect?: (question: string) => void;
  isLoading?: boolean;
}

const ROLE_LABELS = {
  layperson: { user: "U", assistant: "Juridisch assistent" },
  professional: { user: "U", assistant: "Assistent" },
} as const;

export function ChatThread({
  messages,
  audience = "layperson",
  conversationId,
  onVerificationSelect,
  isLoading = false,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const clarificationRef = useRef<HTMLDivElement>(null);
  const labels = ROLE_LABELS[audience];
  const lastClarificationMessageId = getActiveClarificationMessageId(messages, audience);

  useEffect(() => {
    if (lastClarificationMessageId && !isLoading) {
      scrollIntoViewRespectingMotion(clarificationRef.current, { block: "nearest" });
      return;
    }
    scrollIntoViewRespectingMotion(bottomRef.current, { block: "end" });
  }, [messages, isLoading, lastClarificationMessageId]);

  return (
    <div className={`${styles.thread} ${chatLayoutStyles.chatThread}`} aria-live="polite">
      {messages.map((msg) => {
        const isClarification = shouldUseClarificationPanel(msg, audience);
        const isActiveClarification = isClarification && msg.id === lastClarificationMessageId;
        const handleSelect = isActiveClarification && !isLoading ? onVerificationSelect : undefined;
        return (
        <div
          key={msg.id}
          ref={isActiveClarification ? clarificationRef : undefined}
          className={`${styles.message} ${msg.role === "user" ? styles.user : ""} ${
            msg.isPending ? styles.pending : ""
          } ${isActiveClarification ? styles.activeClarification : ""}`}
        >
          <span className={styles.role} aria-hidden="true">
            {msg.role === "user" ? labels.user : labels.assistant.slice(0, 2)}
          </span>
          <div className={styles.bubble}>
            {msg.isPending ? (
              <p className={styles.typing}>Bezig met antwoorden…</p>
            ) : msg.role === "assistant" ? (
              <div className={styles.text}>
                {msg.legalHypothesis && audience === "professional" && !isClarification && (
                  <LegalHypothesisPanel hypothesis={msg.legalHypothesis} audience={audience} />
                )}
                {isActiveClarification && msg.verificationQuestions ? (
                  <ClarificationPanel
                    intro={msg.content}
                    prompt={msg.clarificationPrompt}
                    options={filterLaypersonClarificationChips(msg.verificationQuestions)}
                    onSelect={handleSelect}
                    isDisabled={isLoading}
                  />
                ) : msg.coverageStatus === "clarify_only" ? (
                  <p className={styles.resolvedClarification}>
                    Verduidelijking ontvangen — zie uw keuze hieronder in het gesprek.
                  </p>
                ) : (
                  <LaypersonMarkdown>{msg.content}</LaypersonMarkdown>
                )}
              </div>
            ) : (
              <p className={styles.text}>{msg.content}</p>
            )}
            {!msg.isPending && msg.citations && msg.citations.length > 0 && (
              <AnswerProvenance citations={msg.citations} audience={audience} />
            )}
            {!msg.isPending && msg.citations && msg.citations.length > 0 && (
              <CitationSources citations={msg.citations} audience={audience} />
            )}
            {!msg.isPending && msg.coverageGuidance && (
              <CoverageGuidancePanel guidance={msg.coverageGuidance} audience={audience} />
            )}
            {!msg.isPending &&
              isActiveClarification &&
              audience === "professional" &&
              msg.verificationQuestions &&
              msg.verificationQuestions.length > 0 && (
              <VerificationQuestions
                questions={msg.verificationQuestions}
                isCoverageGap={msg.coverageStatus !== "adequate" && !!msg.coverageStatus}
                onSelectQuestion={handleSelect}
                isDisabled={isLoading}
              />
            )}
            {!msg.isPending && msg.role === "assistant" && !isClarification && (
              <FeedbackPanel conversationId={conversationId} messageId={msg.id} />
            )}
          </div>
        </div>
      );
      })}
      <div ref={bottomRef} className={styles.scrollAnchor} />
    </div>
  );
}
