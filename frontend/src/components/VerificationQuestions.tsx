"use client";

import styles from "./VerificationQuestions.module.css";

interface Props {
  questions: string[];
}

export function VerificationQuestions({ questions }: Props) {
  if (questions.length === 0) return null;

  return (
    <aside className={styles.panel} aria-label="Controlevragen bij onzeker antwoord">
      <p className={styles.title}>Ter controle — kunt u dit bevestigen?</p>
      <ul className={styles.list}>
        {questions.map((question) => (
          <li key={question}>{question}</li>
        ))}
      </ul>
    </aside>
  );
}
