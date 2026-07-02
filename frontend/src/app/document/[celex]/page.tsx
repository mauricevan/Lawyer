"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { LegalFooter } from "@/components/LegalFooter";
import { TrustCard } from "@/components/TrustCard";
import { getDocument } from "@/services/queryService";
import type { Citation } from "@/models/types";
import styles from "./page.module.css";

interface DocumentVersion {
  celex: string;
  title: string;
  language: string;
  is_consolidated: boolean;
  is_in_force: boolean;
  version_type: string;
  oj_reference?: string;
  eurlex_url: string;
}

interface DocumentData {
  celex: string;
  versions: DocumentVersion[];
  relations: Record<string, string>[];
  eurlex_url: string;
}

export default function DocumentPage() {
  const params = useParams();
  const celex = params.celex as string;
  const [doc, setDoc] = useState<DocumentData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDocument(celex)
      .then(setDoc)
      .catch(() => setError("Document niet gevonden"));
  }, [celex]);

  if (error) {
    return (
      <main className="container">
        <p role="alert">{error}</p>
        <Link href="/">Terug naar home</Link>
      </main>
    );
  }

  if (!doc) {
    return (
      <main className="container">
        <p>Document laden...</p>
      </main>
    );
  }

  const primary = doc.versions[0];

  return (
    <main className="container">
      <header className={styles.header}>
        <Link href="/" className={styles.back}>
          ← Terug
        </Link>
        <h1 className={styles.title}>{primary?.title || celex}</h1>
        <p className={styles.celex}>CELEX: {celex}</p>
        <a
          href={doc.eurlex_url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.eurlexLink}
        >
          Bekijk op EUR-Lex →
        </a>
      </header>

      {primary && (
        <TrustCard
          citation={{
            celex,
            title: primary.title,
            excerpt: "",
            eurlex_url: primary.eurlex_url,
            legal_citation: primary.title,
            trust: {
              is_consolidated: primary.is_consolidated,
              is_in_force: primary.is_in_force,
              oj_reference: primary.oj_reference,
              has_corrigendum: primary.version_type === "corrigendum",
            },
          } as Citation}
        />
      )}

      <section className={styles.section}>
        <h2>Alle versies ({doc.versions.length})</h2>
        <ul className={styles.versionList}>
          {doc.versions.map((v) => (
            <li key={v.celex} className={styles.versionItem}>
              <span className={styles.versionType}>{v.version_type}</span>
              <span>{v.title}</span>
              {v.is_consolidated && (
                <span className={styles.badge}>Geconsolideerd</span>
              )}
              <a href={v.eurlex_url} target="_blank" rel="noopener noreferrer">
                EUR-Lex
              </a>
            </li>
          ))}
        </ul>
      </section>

      {doc.relations.length > 0 && (
        <section className={styles.section}>
          <h2>Gerelateerde documenten</h2>
          <ul className={styles.relationList}>
            {doc.relations.map((rel, i) => (
              <li key={i}>
                {rel.relation}: {rel.target}
              </li>
            ))}
          </ul>
        </section>
      )}

      <LegalFooter />
    </main>
  );
}
