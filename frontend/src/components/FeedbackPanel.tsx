"use client";

import { useState } from "react";
import type { FeedbackCategory } from "@/models/types";
import { FEEDBACK_CATEGORIES, submitFeedback } from "@/services/feedbackApi";
import styles from "./FeedbackPanel.module.css";

interface Props {
  conversationId?: string;
  messageId: string;
}

type PanelState = "idle" | "negative" | "submitting" | "done" | "error";

export function FeedbackPanel({ conversationId, messageId }: Props) {
  const [state, setState] = useState<PanelState>("idle");
  const [comment, setComment] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const sendFeedback = async (rating: number, category?: FeedbackCategory) => {
    setState("submitting");
    setErrorMessage(null);
    try {
      await submitFeedback({
        rating,
        category,
        comment: comment.trim() || undefined,
        conversation_id: conversationId,
      });
      setState("done");
    } catch {
      setState("error");
      setErrorMessage("Feedback kon niet worden verstuurd. Probeer het later opnieuw.");
    }
  };

  if (state === "done") {
    return (
      <p className={styles.thanks} role="status">
        Bedankt voor uw feedback.
      </p>
    );
  }

  return (
    <div className={styles.panel} aria-label="Feedback op dit antwoord">
      {state === "idle" && (
        <div className={styles.row}>
          <span className={styles.prompt}>Heeft dit geholpen?</span>
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.primaryBtn}
              onClick={() => sendFeedback(5, "positive")}
            >
              Ja
            </button>
            <button
              type="button"
              className={styles.secondaryBtn}
              onClick={() => setState("negative")}
            >
              Nee
            </button>
          </div>
        </div>
      )}

      {state === "negative" && (
        <div className={styles.negativeFlow}>
          <p className={styles.prompt}>Wat ging er mis?</p>
          <div className={styles.categoryGrid}>
            {FEEDBACK_CATEGORIES.map((item) => (
              <button
                key={`${messageId}-${item.id}`}
                type="button"
                className={styles.categoryBtn}
                onClick={() => sendFeedback(item.rating, item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <label className={styles.commentLabel} htmlFor={`feedback-comment-${messageId}`}>
            Toelichting (optioneel)
          </label>
          <textarea
            id={`feedback-comment-${messageId}`}
            className={styles.comment}
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            maxLength={1000}
            rows={2}
            placeholder="Bijv. welke bron ontbrak?"
          />
        </div>
      )}

      {state === "submitting" && <p className={styles.submitting}>Versturen...</p>}

      {state === "error" && errorMessage && (
        <p className={styles.error} role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
