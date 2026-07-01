"use client";

import { useState } from "react";
import type { Citation } from "@/models/types";
import styles from "./CopyCitationButton.module.css";

interface Props {
  citation: Citation;
}

export function CopyCitationButton({ citation }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const text =
      citation.legal_citation ||
      `Artikel ${citation.article}, ${citation.title || citation.celex}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button type="button" className={styles.button} onClick={handleCopy}>
      {copied ? "Gekopieerd!" : "Kopieer citaat"}
    </button>
  );
}
