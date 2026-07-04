"use client";

import { useEffect, useState } from "react";
import styles from "./VerificationQuestions.module.css";

interface Props {
  questions: string[];
  isCoverageGap?: boolean;
  onSelectQuestion?: (question: string) => void;
}

export function VerificationQuestions({
  questions,
  isCoverageGap = false,
  onSelectQuestion,
}: Props) {
  const [activeQuestion, setActiveQuestion] = useState<string | null>(null);

  useEffect(() => {
    setActiveQuestion(null);
  }, [questions]);

  if (questions.length === 0) return null;

  const title = isCoverageGap
    ? "Om u beter te helpen"
    : "Ter controle — kunt u dit bevestigen?";

  const handleSelect = (question: string) => {
    setActiveQuestion(question);
    onSelectQuestion?.(question);
  };

  return (
    <aside className={styles.panel} aria-label={title}>
      <p className={styles.title}>{title}</p>
      {onSelectQuestion ? (
        <div className={styles.chips} role="list">
          {questions.map((question) => (
            <button
              key={question}
              type="button"
              role="listitem"
              className={styles.chip}
              aria-pressed={activeQuestion === question}
              onClick={() => handleSelect(question)}
            >
              {question}
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
