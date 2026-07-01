import type { Citation } from "@/models/types";
import styles from "./SourcesSidebar.module.css";

interface Props {
  citations: Citation[];
}

export function SourcesSidebar({ citations }: Props) {
  if (citations.length === 0) return null;

  return (
    <aside className={styles.sidebar} aria-label="Bronnen">
      <h2 className={styles.title}>Bronnen ({citations.length})</h2>
      <ul className={styles.list}>
        {citations.map((cite, i) => (
          <li key={`${cite.celex}-${i}`} className={styles.item}>
            <a href={`/document/${cite.celex}`} className={styles.docLink}>
              {cite.title || cite.celex}
            </a>
            {cite.article && (
              <span className={styles.article}>Art. {cite.article}</span>
            )}
            <a
              href={cite.eurlex_url}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.eurlexLink}
            >
              EUR-Lex →
            </a>
          </li>
        ))}
      </ul>
    </aside>
  );
}
