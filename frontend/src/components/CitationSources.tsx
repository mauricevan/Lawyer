"use client";

import { useState } from "react";
import type { Audience, Citation } from "@/models/types";
import { TrustCard } from "./TrustCard";
import styles from "./CitationSources.module.css";

const LABELS = {
  layperson: {
    show: "Bekijk de verordeningen",
    hide: "Verberg verordeningen",
  },
  professional: {
    show: "Bekijk bronnen",
    hide: "Verberg bronnen",
  },
} as const;

interface Props {
  citations: Citation[];
  audience?: Audience;
}

export function CitationSources({ citations, audience = "layperson" }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const labels = LABELS[audience];

  if (citations.length === 0) return null;

  return (
    <div>
      <button
        type="button"
        className={styles.toggle}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
      >
        {isOpen ? labels.hide : labels.show} ({citations.length})
      </button>
      {isOpen && (
        <div className={styles.list}>
          {citations.map((cite, i) => (
            <TrustCard
              key={`${cite.celex}-${cite.article}-${i}`}
              citation={cite}
              audience={audience}
            />
          ))}
        </div>
      )}
    </div>
  );
}
