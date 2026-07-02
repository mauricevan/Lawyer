"use client";

import Link from "next/link";
import type { Audience, SupportedLanguage } from "@/models/types";
import { getDisclaimer, getEscalationText } from "@/content/legalDisclaimers";
import styles from "./LegalFooter.module.css";

interface Props {
  audience?: Audience;
  language?: SupportedLanguage;
  compact?: boolean;
}

export function LegalFooter({
  audience = "layperson",
  language = "nl",
  compact = false,
}: Props) {
  return (
    <footer className={compact ? styles.compact : styles.footer} aria-label="Juridische informatie">
      <p className={styles.disclaimer}>{getDisclaimer(audience, language)}</p>
      {!compact && (
        <>
          <p className={styles.escalation}>{getEscalationText(audience, language)}</p>
          <Link className={styles.link} href="/juridische-informatie">
            Beperkingen en escalatiepad
          </Link>
        </>
      )}
    </footer>
  );
}
