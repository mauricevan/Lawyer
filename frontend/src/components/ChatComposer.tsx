"use client";

import { useRef, type FormEvent, type KeyboardEvent } from "react";
import styles from "./ChatComposer.module.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (text: string) => void;
  isLoading?: boolean;
  isFollowUp?: boolean;
  label?: string;
  variant?: "landing" | "sticky";
}

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  isLoading = false,
  isFollowUp = false,
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

  const placeholder = isFollowUp
    ? "Stel een vervolgvraag..."
    : "Beschrijf kort uw situatie of wat u wilt weten...";

  const wrapperClass =
    variant === "landing"
      ? `${styles.composer} ${styles.composerLanding}`
      : `${styles.composer} ${styles.composerSticky}`;

  const inputClass = isFollowUp
    ? `${styles.input} ${styles.inputCompact}`
    : styles.input;

  return (
    <div className={wrapperClass}>
      <div className={styles.inner}>
        {label && (
          <label htmlFor="chat-input" className={styles.label}>
            {label}
          </label>
        )}
        <form onSubmit={handleSubmit} className={styles.form}>
          <textarea
            ref={textareaRef}
            id="chat-input"
            className={inputClass}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={isFollowUp ? 2 : 3}
            disabled={isLoading}
            aria-label={label || "Uw vraag"}
          />
          <button
            type="submit"
            className={styles.submit}
            disabled={isLoading || !value.trim()}
          >
            {isLoading ? "..." : isFollowUp ? "Verstuur" : "Stel vraag"}
          </button>
        </form>
      </div>
    </div>
  );
}
