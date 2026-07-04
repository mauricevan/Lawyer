"use client";

import type { Audience, RetrievalEvent } from "@/models/types";
import { parseLegalHypothesis } from "@/utils/legalHypothesisLabels";
import { useEffect, useMemo, useState } from "react";
import { LegalHypothesisPanel } from "./LegalHypothesisPanel";
import styles from "./RetrievalStatus.module.css";

const STEP_LABELS: Record<string, string> = {
  hypothesis: "Analyse",
  conflict: "Conflict",
  celex: "EU-bronnen",
  planning: "Kaders",
  resolving: "Wetgeving",
  fetching: "EUR-Lex",
  validating: "Bewijs",
  reconciling: "Afstemming",
  verifying: "Controle",
  search: "Zoeken",
  router: "Router",
  found: "Gevonden",
  versions: "Versies",
  generating: "Samenstellen",
  complete: "Klaar",
};

const DEFAULT_MESSAGES: Record<Audience, string> = {
  layperson: "Ik bekijk de relevante EU-regels...",
  professional: "Zoeken in EU-documenten...",
};

interface Props {
  events: RetrievalEvent[];
  isLoading: boolean;
  audience?: Audience;
  onCancel?: () => void;
  cancelAfterMs?: number;
}

function hypothesisFromEvents(events: RetrievalEvent[]) {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index];
    if (!event.detail) continue;
    const parsed = parseLegalHypothesis(event.detail.legal_hypothesis);
    if (parsed) return parsed;
  }
  return undefined;
}

export function RetrievalStatus({
  events,
  isLoading,
  audience = "layperson",
  onCancel,
  cancelAfterMs = 10_000,
}: Props) {
  const [showCancel, setShowCancel] = useState(false);
  const liveHypothesis = useMemo(() => hypothesisFromEvents(events), [events]);

  useEffect(() => {
    if (!isLoading) {
      setShowCancel(false);
      return undefined;
    }
    const timer = window.setTimeout(() => setShowCancel(true), cancelAfterMs);
    return () => window.clearTimeout(timer);
  }, [isLoading, cancelAfterMs]);

  if (!isLoading && events.length === 0) return null;

  const displayEvents =
    events.length > 0
      ? events
      : [{ step: "search", message: DEFAULT_MESSAGES[audience] }];

  return (
    <div className={styles.container} aria-live="polite" aria-busy={isLoading}>
      {liveHypothesis && (
        <LegalHypothesisPanel
          hypothesis={liveHypothesis}
          audience={audience}
          compact
          isLoading={isLoading}
        />
      )}
      <ul className={styles.list}>
        {displayEvents.map((event, i) => (
          <li key={`${event.step}-${i}`} className={styles.item}>
            <span className={styles.icon} aria-hidden="true">
              {STEP_LABELS[event.step] || "Stap"}
            </span>
            <span>{event.message}</span>
          </li>
        ))}
      </ul>
      {isLoading && showCancel && onCancel && (
        <button type="button" className={styles.cancelBtn} onClick={onCancel}>
          Annuleren
        </button>
      )}
    </div>
  );
}
