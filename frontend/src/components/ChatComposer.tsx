"use client";

import { useRef, type FormEvent, type KeyboardEvent } from "react";
import { CLARIFICATION_INPUT_HINT_ID } from "@/utils/clarificationView";
import styles from "./ChatComposer.module.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (text: string) => void;
  isLoading?: boolean;
  isFollowUp?: boolean;
  isClarificationFollowUp?: boolean;
  label?: string;
  variant?: "landing" | "sticky";
}

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  isLoading = false,
  isFollowUp = false,
  isClarificationFollowUp = false,
  label,
  variant = "sticky",
}: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSubmit(value.trim());
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!value.trim() || isLoading) return;
      onSubmit(value.trim());
    }
  };

  const placeholder = isClarificationFollowUp
    ? "Bijv. marktplaats voor particulieren in de EU…"
    : isFollowUp
      ? "Stel een vervolgvraag…"
      : "Beschrijf kort uw situatie of wat u wilt weten…";

  const resolvedLabel =
    label ?? (isClarificationFollowUp ? "Of Typ Hier Uw Antwoord" : undefined);

  const wrapperClass = [
    styles.composer,
    variant === "landing" ? styles.composerLanding : styles.composerSticky,
    isClarificationFollowUp ? styles.composerClarification : "",
  ]
    .filter(Boolean)
    .join(" ");

  const inputClass = [
    styles.input,
    isFollowUp ? styles.inputCompact : "",
    isClarificationFollowUp ? styles.inputClarification : "",
  ]
    .filter(Boolean)
    .join(" ");

  const submitLabel = isLoading
    ? "Versturen…"
    : isFollowUp
      ? "Verstuur"
      : "Stel Vraag";

  return (
    <div className={wrapperClass}>
      <div className={styles.inner}>
        {resolvedLabel && (
          <label htmlFor="chat-input" className={styles.label}>
            {resolvedLabel}
          </label>
        )}
        <form onSubmit={handleSubmit} className={styles.form}>
          <textarea
            ref={textareaRef}
            id="chat-input"
            name="question"
            className={inputClass}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={isFollowUp ? 2 : 3}
            disabled={isLoading}
            autoComplete="off"
            aria-label={resolvedLabel || "Uw vraag"}
            aria-describedby={isClarificationFollowUp ? CLARIFICATION_INPUT_HINT_ID : undefined}
          />
          <button
            type="submit"
            className={styles.submit}
            disabled={isLoading || !value.trim()}
          >
            {submitLabel}
          </button>
        </form>
      </div>
    </div>
  );
}
