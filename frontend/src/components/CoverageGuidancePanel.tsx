"use client";

import type { Audience, CoverageGuidance } from "@/models/types";
import styles from "./CoverageGuidancePanel.module.css";

interface Props {
  guidance: CoverageGuidance;
  audience?: Audience;
}

export function CoverageGuidancePanel({ guidance, audience = "layperson" }: Props) {
  const isCompact = audience === "professional";

  return (
    <aside
      className={`${styles.panel} ${isCompact ? styles.compact : ""}`}
      aria-label="Doorverwijzingen en relevante regelgeving"
    >
      <p className={styles.title}>
        {audience === "layperson"
          ? "Waar u verder kunt zoeken"
          : "Aanvullende kaders buiten corpus"}
      </p>
      {guidance.frameworks.length > 0 && (
        <>
          <p className={styles.sectionTitle}>Relevante regelgeving</p>
          <ul className={styles.frameworkList}>
            {guidance.frameworks.map((item) => (
              <li key={item.name}>
                <span className={styles.frameworkName}>{item.name}</span>
                {": "}
                {item.summary}
              </li>
            ))}
          </ul>
        </>
      )}
      {guidance.referrals.length > 0 && (
        <>
          <p className={styles.sectionTitle}>Instanties</p>
          <ul className={styles.referralList}>
            {guidance.referrals.map((item) => (
              <li key={item.url}>
                <a
                  href={item.url}
                  className={styles.referralLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </>
      )}
    </aside>
  );
}
