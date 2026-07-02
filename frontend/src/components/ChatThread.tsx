"use client";

import { useEffect, useRef } from "react";
import Markdown from "react-markdown";
import type { Audience, ChatMessage } from "@/models/types";
import { CitationSources } from "./CitationSources";
import { FeedbackPanel } from "./FeedbackPanel";
import styles from "./ChatThread.module.css";

interface Props {
  messages: ChatMessage[];
  audience?: Audience;
  conversationId?: string;
}

const ROLE_LABELS = {
  layperson: { user: "U", assistant: "Juridisch assistent" },
  professional: { user: "U", assistant: "Assistent" },
} as const;

export function ChatThread({ messages, audience = "layperson", conversationId }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const labels = ROLE_LABELS[audience];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className={styles.thread} aria-live="polite">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`${styles.message} ${msg.role === "user" ? styles.user : ""} ${
            msg.isPending ? styles.pending : ""
          }`}
        >
          <span className={styles.role} aria-hidden="true">
            {msg.role === "user" ? labels.user : labels.assistant.slice(0, 2)}
          </span>
          <div className={styles.bubble}>
            {msg.isPending ? (
              <p className={styles.typing}>Bezig met antwoorden...</p>
            ) : msg.role === "assistant" ? (
              <div className={styles.text}>
                <Markdown>{msg.content}</Markdown>
              </div>
            ) : (
              <p className={styles.text}>{msg.content}</p>
            )}
            {!msg.isPending && msg.citations && msg.citations.length > 0 && (
              <CitationSources citations={msg.citations} audience={audience} />
            )}
            {!msg.isPending && msg.role === "assistant" && (
              <FeedbackPanel conversationId={conversationId} messageId={msg.id} />
            )}
          </div>
        </div>
      ))}
      <div ref={bottomRef} className={styles.scrollAnchor} />
    </div>
  );
}
