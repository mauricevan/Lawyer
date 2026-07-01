import styles from "./ExampleQuestions.module.css";

interface Props {
  questions: string[];
  onSelect: (question: string) => void;
  title?: string;
}

export function ExampleQuestions({
  questions,
  onSelect,
  title = "Voorbeeldvragen",
}: Props) {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{title}</h2>
      <ul className={styles.list}>
        {questions.map((q) => (
          <li key={q}>
            <button type="button" className={styles.button} onClick={() => onSelect(q)}>
              {q}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
