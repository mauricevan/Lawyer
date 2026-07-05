"use client";

import type { Audience, RetrievalEvent } from "@/models/types";
import { parseLegalHypothesis } from "@/utils/legalHypothesisLabels";
import { useEffect, useMemo, useState } from "react";
import { LegalHypothesisPanel } from "./LegalHypothesisPanel";
import styles from "./RetrievalStatus.module.css";

const LAYPERSON_VISIBLE_STEPS = new Set([
  "clarifying",
  "clarified",
  "fetching",
  "validating",
  "generating",
  "complete",
  "search",
  "found",
  "verifying",
]);

const LAYPERSON_STEP_LABELS: Record<string, string> = {
  clarifying: "Vraag verduidelijken",
  clarified: "Vraag helder",
  fetching: "EUR-Lex",
  validating: "Bronnen controleren",
  generating: "Antwoord samenstellen",
  complete: "Klaar",
  search: "Zoeken",
  found: "Gevonden",
  verifying: "Controle",
};

const STEP_LABELS: Record<string, string> = {
  hypothesis: "Analyse",
  conflict: "Conflict",
  effect: "Juridisch effect",
  celex: "EU-bronnen",
  planning: "Kaders",
  resolving: "Wetgeving",
  fetching: "EUR-Lex",
  validating: "Bewijs",
  reconciling: "Afstemming",
  judge: "Juridische toets",
  judged: "Toets klaar",
  court: "Hof-simulatie",
  simulated: "Simulatie klaar",
  panel: "Panelbesluit",
  finalized: "Besluit klaar",
  doctrine: "Doctrine-evolutie",
  evolved: "Evolutie klaar",
  anchoring: "Doctrine-ankers",
  anchored: "Ankers klaar",
  clarifying: "Vraag verduidelijken",
  clarified: "Vraag helder",
  stability: "Doctrine-stabiliteit",
  stabilized: "Stabiliteit klaar",
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
  isHidden?: boolean;
  compact?: boolean;
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
  isHidden = false,
  compact = false,
}: Props) {
  const [showCancel, setShowCancel] = useState(false);
  const liveHypothesis = useMemo(() => hypothesisFromEvents(events), [events]);
  const hideHypothesis = audience === "layperson";

  useEffect(() => {
    if (!isLoading) {
      setShowCancel(false);
      return undefined;
    }
    const timer = window.setTimeout(() => setShowCancel(true), cancelAfterMs);
    return () => window.clearTimeout(timer);
  }, [isLoading, cancelAfterMs]);

  if (isHidden) return null;
  if (!isLoading && events.length === 0) return null;

  const filteredEvents =
    audience === "layperson"
      ? events.filter((event) => LAYPERSON_VISIBLE_STEPS.has(event.step))
      : events;

  if (!isLoading && audience === "layperson" && filteredEvents.length === 0) return null;

  const displayEvents =
    filteredEvents.length > 0
      ? filteredEvents
      : [{ step: "search", message: DEFAULT_MESSAGES[audience] }];
  const visibleEvents = compact && isLoading ? displayEvents.slice(-1) : displayEvents;

  return (
    <div
      className={`${styles.container} ${compact ? styles.containerCompact : ""}`}
      aria-live="polite"
      aria-busy={isLoading}
    >
      {liveHypothesis && !hideHypothesis && (
        <LegalHypothesisPanel
          hypothesis={liveHypothesis}
          audience={audience}
          compact
          isLoading={isLoading}
        />
      )}
      <ul className={styles.list}>
        {visibleEvents.map((event, i) => (
          <li key={`${event.step}-${i}`} className={styles.item}>
            <span className={styles.icon} aria-hidden="true">
              {(audience === "layperson" ? LAYPERSON_STEP_LABELS : STEP_LABELS)[event.step] || "Stap"}
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
