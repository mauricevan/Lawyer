"use client";

import { formatChoiceLabel } from "@/utils/formatChoiceLabel";
import styles from "./VerificationQuestions.module.css";

interface Props {
  questions: string[];
  isCoverageGap?: boolean;
  onSelectQuestion?: (question: string) => void;
  isDisabled?: boolean;
}

export function VerificationQuestions({
  questions,
  isCoverageGap = false,
  onSelectQuestion,
  isDisabled = false,
}: Props) {
  if (questions.length === 0) return null;

  const title = isCoverageGap
    ? "Om U Beter Te Helpen — Klik Om Direct Door Te Gaan"
    : "Ter Controle — Klik Om Direct Door Te Gaan";

  const handleSelect = (question: string) => {
    if (isDisabled) return;
    onSelectQuestion?.(question);
  };

  return (
    <aside className={styles.panel} aria-label={title}>
      <p className={styles.title}>{title}</p>
      {onSelectQuestion ? (
        <div className={styles.chips}>
          {questions.map((question) => (
            <button
              key={question}
              type="button"
              className={styles.chip}
              disabled={isDisabled}
              onClick={() => handleSelect(question)}
            >
              {formatChoiceLabel(question)}
            </button>
          ))}
        </div>
      ) : (
        <ul className={styles.list}>
          {questions.map((question) => (
            <li key={question}>{question}</li>
          ))}
        </ul>
      )}
    </aside>
  );
}
