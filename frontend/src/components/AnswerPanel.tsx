import Markdown from "react-markdown";
import type { AnswerResponse, Audience } from "@/models/types";
import { getDisclaimer } from "@/content/legalDisclaimers";
import { CitationSources } from "./CitationSources";
import styles from "./AnswerPanel.module.css";

interface Props {
  question: string;
  response: AnswerResponse;
  audience?: Audience;
}

const LABELS = {
  layperson: {
    answer: "Dit betekent voor u",
    sources: "Waar dit op gebaseerd is",
  },
  professional: {
    answer: "Antwoord",
    sources: "Bronnen",
  },
} as const;

export function AnswerPanel({ question, response, audience = "layperson" }: Props) {
  const labels = LABELS[audience];
  const disclaimer = response.disclaimer || getDisclaimer(audience);

  return (
    <section className={styles.panel} aria-live="polite">
      <div className={styles.questionBlock}>
        <span className={styles.label}>Uw vraag</span>
        <p className={styles.question}>{question}</p>
      </div>

      <div className={styles.answerBlock}>
        <h2 className={styles.title}>{labels.answer}</h2>
        <div className={styles.answer}>
          <Markdown>{response.answer}</Markdown>
        </div>
      </div>

      {response.citations.length > 0 && (
        <CitationSources citations={response.citations} audience={audience} />
      )}

      <p className={styles.disclaimer}>{disclaimer}</p>
    </section>
  );
}
