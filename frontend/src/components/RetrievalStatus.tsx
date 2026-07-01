import type { Audience, RetrievalEvent } from "@/models/types";
import styles from "./RetrievalStatus.module.css";

const STEP_ICONS: Record<string, string> = {
  search: "🔍",
  found: "📄",
  versions: "⚖️",
  generating: "✍️",
  complete: "✅",
};

const DEFAULT_MESSAGES: Record<Audience, string> = {
  layperson: "Ik bekijk de relevante EU-regels...",
  professional: "Zoeken in EU-documenten...",
};

interface Props {
  events: RetrievalEvent[];
  isLoading: boolean;
  audience?: Audience;
}

export function RetrievalStatus({ events, isLoading, audience = "layperson" }: Props) {
  if (!isLoading && events.length === 0) return null;

  const displayEvents =
    events.length > 0
      ? events
      : [{ step: "search", message: DEFAULT_MESSAGES[audience] }];

  return (
    <div className={styles.container} aria-live="polite" aria-busy={isLoading}>
      <ul className={styles.list}>
        {displayEvents.map((event, i) => (
          <li key={`${event.step}-${i}`} className={styles.item}>
            <span className={styles.icon}>{STEP_ICONS[event.step] || "•"}</span>
            <span>{event.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
