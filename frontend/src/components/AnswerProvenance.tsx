"use client";

import { useEffect, useMemo, useState } from "react";
import type { Audience, Citation } from "@/models/types";
import styles from "./AnswerProvenance.module.css";

interface CorpusSummary {
  last_indexed_at?: string | null;
}

interface Props {
  citations: Citation[];
  audience?: Audience;
}

function formatArticles(citations: Citation[]): string {
  const articles = [
    ...new Set(citations.map((c) => c.article).filter(Boolean) as string[]),
  ];
  return articles.length > 0 ? articles.join(", ") : "—";
}

function primarySource(citations: Citation[], audience: Audience): string {
  if (citations.length === 0) return "Geen geïndexeerde bron";
  const first = citations[0];
  if (audience === "layperson") {
    return first.title || "EU-regelgeving";
  }
  return first.title || first.celex;
}

export function AnswerProvenance({ citations, audience = "layperson" }: Props) {
  const [corpus, setCorpus] = useState<CorpusSummary | null>(null);
  const sourceLabel = useMemo(
    () => primarySource(citations, audience),
    [citations, audience],
  );
  const articleLabel = useMemo(() => formatArticles(citations), [citations]);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8003";
    fetch(`${base}/api/v1/documents/corpus/summary`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setCorpus(data))
      .catch(() => setCorpus(null));
  }, []);

  const lastUpdate = corpus?.last_indexed_at
    ? new Date(corpus.last_indexed_at).toLocaleDateString("nl-NL")
    : null;

  return (
    <aside className={styles.banner} aria-label="Bronverificatie">
      <p className={styles.title}>
        Gebaseerd op: {sourceLabel}
        {citations.length > 0 && (
          <span className={styles.verified}> — Gecontroleerde bron ✓</span>
        )}
      </p>
      <p className={styles.meta}>Artikelen gevonden: {articleLabel}</p>
      {lastUpdate && (
        <p className={styles.meta}>Laatste update kennisbank: {lastUpdate}</p>
      )}
    </aside>
  );
}
