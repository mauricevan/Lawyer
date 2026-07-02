"use client";

import Link from "next/link";
import type { Audience } from "@/models/types";
import { getDisclaimer, getEscalationText } from "@/content/legalDisclaimers";
import styles from "./LegalFooter.module.css";

interface Props {
  audience?: Audience;
  compact?: boolean;
}

export function LegalFooter({ audience = "layperson", compact = false }: Props) {
  return (
    <footer className={compact ? styles.compact : styles.footer} aria-label="Juridische informatie">
      <p className={styles.disclaimer}>{getDisclaimer(audience)}</p>
      {!compact && (
        <>
          <p className={styles.escalation}>{getEscalationText(audience)}</p>
          <Link className={styles.link} href="/juridische-informatie">
            Beperkingen en escalatiepad
          </Link>
        </>
      )}
    </footer>
  );
}
